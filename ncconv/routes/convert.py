from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, Request
from fastapi.responses import ORJSONResponse
from pydantic import BaseModel, confloat, constr
from bson import ObjectId
from bson.errors import InvalidId

from ncconv.config import DEFAULT_TEMPO, DEFAULT_PITCH
from ncconv.ratelimit import ratelimit

convert_router = APIRouter(prefix='/convert', default_response_class=ORJSONResponse)


class EnqueueResponse(BaseModel):
    task_id: str


@convert_router.post('/', response_model=EnqueueResponse, status_code=202, dependencies=[Depends(ratelimit('do_conversion', 5, timedelta(minutes=5)))])
async def convert_audio_file(request: Request, audio_file: UploadFile = File(...), 
                            output_format: constr(regex='ogg|m4a') = Form(...),
                            scale_pitch: confloat(gt=0, le=10) = Form(DEFAULT_PITCH),
                            scale_tempo: confloat(gt=0, le=10) = Form(DEFAULT_TEMPO)) -> EnqueueResponse:
    '''
    enqueues the audio file to the user's specification and returns a key that be used with /check

    Warning: Length is not checked. Must enforce in NGINX

    :param audio_file: The audio file to process
    :param output_format: The desired output format
    :param scale_pitch: pitch scale factor
    :param scale_tempo: tempo scale factor
    '''

    deadline = datetime.now(timezone.utc) + timedelta(days=1)

    async with request.app.state.file_store.open_upload_stream(audio_file.filename, metadata = {
        'pending': True,
        'expire_time': deadline
    }) as grid_in:
        while (r := await audio_file.read(250 * 1024)):
            await grid_in.write(r)

    task_id = await request.app.state.db.queue.insert_one({
        'pending_file': grid_in._id,
        'scale_pitch': scale_pitch,
        'scale_tempo': scale_tempo,
        'output_format': output_format,
        'expire_time': deadline,
        'enqueued_by': str(request.client.host),
        'state': 0
    })

    return EnqueueResponse(task_id=str(task_id.inserted_id))


class CheckResponse(BaseModel):
    complete: bool
    position: Optional[int]  # if not completed
    file_id: Optional[str]  # if completed


@convert_router.get('/check', response_model=CheckResponse, response_model_exclude_none=True, response_model_exclude_unset=True, dependencies=[Depends(ratelimit('check_status', 5, timedelta(seconds=5)))])
async def check(request: Request, task_id: str):
    '''
    Retrieve information about the enqueued task.

    If the task is completed, this retrieves the converted file_id and deletes the task
    If the task is pending, this retrieves the "position in line"
    If the task has failed, this throws an error

    :param task_id: The task to check
    '''
    try:
        task_id = ObjectId(task_id)
    except InvalidId as e:
        raise HTTPException(status_code=400, detail='Bad object ID') from e


    doc = await request.app.state.db.queue.find_one({'_id': task_id})
    if not doc:
        raise HTTPException(status_code=404, detail='No such task was found.')
    

    if doc['state'] == 2:
        await request.app.state.db.queue.delete_one({'_id': task_id})
        return CheckResponse(complete = True, file_id = str(doc['completed_file']))
    elif doc['state'] == 3:
        await request.app.state.db.queue.delete_one({'_id': task_id})
        raise HTTPException(status_code=doc['status_code'], detail=doc['detail'])
    elif doc['state'] > 3:
        raise HTTPException(status_code=500, detail='Request is in a bad state. Try making a new one!')

    
    # _id encodes a 4 byte timestamp, so it can be used to roughly guess how many documents are ahead of us
    # anything with an _id less the doc['_id'] would have be submitted before us
    ahead = (await request.app.state.db.queue.count_documents({'_id': {'$lt': doc['_id']}, 'state': {'$lte': 1}}))
    return CheckResponse(complete = False, position = ahead + 1)