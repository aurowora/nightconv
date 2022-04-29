# Route handler for downloading content

from datetime import datetime
from typing import List
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import ORJSONResponse
from pydantic import BaseModel
from starlette.responses import StreamingResponse
from bson import ObjectId
from bson.errors import InvalidId
from gridfs.errors import NoFile

media_router = APIRouter(prefix='/media')

@media_router.get('/file/{file_id}/{filename}')
async def get_file(ctx: Request, file_id: str, filename: str) -> StreamingResponse:
    '''
    Retrieves a file from GridFS with the specified file_id.

    :param file_id: ObjectID represented as a string
    :param filename: Necessary to stop the browser from giving the file the wrong extension
    '''

    try:
        file_id = ObjectId(file_id)
    except InvalidId as e:
        raise HTTPException(status_code=400, detail='Audio file ID is not valid') from e
    
    try:
        grid_out = await ctx.app.state.file_store.open_download_stream(file_id)
    except NoFile as e:
        raise HTTPException(status_code=404, detail='Audio file expired or never existed.') from e

    if 'pending' in grid_out.metadata:
        raise HTTPException(status_code=404, detail='Audio file expired or never existed.')

    content_type = grid_out.metadata['content_type']

    async def reader():
        while grid_out.tell() < grid_out.length:
            yield await grid_out.readchunk()
    
    return StreamingResponse(reader(), media_type=content_type, headers={
        'Content-Disposition': f'attachment; filename="{grid_out.filename}"',
        'Cache-Control': 'public, max-age=31536000, immutable, no-transform',
        'Content-Length': str(grid_out.length)
    })


class FileDescription(BaseModel):
    filename: str
    content_type: str
    expire_time: datetime
    length: int


@media_router.get('/describe/{file_id}', response_class=ORJSONResponse)
async def get_file(ctx: Request, file_id: str) -> FileDescription:
    '''
    Retrieves basic infomration about a GridFS object. Is needed by the front end to actually stream the object.

    :param file_id: ObjectID represented as a string.
    '''
    try:
        file_id = ObjectId(file_id)
    except InvalidId as e:
        raise HTTPException(status_code=400, detail='Audio file ID is not valid') from e

    fi = await ctx.app.state.db.music.files.find_one({'_id': file_id, '$or': [{'metadata.pending': {'$exists': False}}, {'metadata.pending': False}]})

    if not fi:
        raise HTTPException(status_code=404, detail='Audio file expired or never existed.')
    
    return FileDescription(filename=fi['filename'], content_type=fi['metadata']['content_type'], expire_time=fi['metadata']['expire_time'], length=fi['length'])


@media_router.get('/recents', response_class=ORJSONResponse)
async def get_recents(ctx: Request) -> List[str]:
    '''
    Retrieves the 10 most recently converted files.
    '''
    
    cur = ctx.app.state.db.music.files.find({'$or': [{'metadata.pending': {'$exists': False}}, {'metadata.pending': False}]})
    cur.sort(('uploadDate'), -1)
    cur.limit(10)

    results = []

    async for doc in cur:
        results.append(str(doc['_id']))

    return results