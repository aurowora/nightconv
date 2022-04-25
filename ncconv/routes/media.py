# Route handler for downloading content

from fastapi import APIRouter, Request, HTTPException
from starlette.responses import StreamingResponse
from bson import ObjectId
from bson.errors import InvalidId
from gridfs.errors import NoFile

media_router = APIRouter(prefix='/media')

@media_router.get('/{file_id}')
async def get_file(ctx: Request, file_id: str) -> StreamingResponse:
    '''
    Retrieves a file from GridFS with the specified file_id.

    :param file_id: ObjectID represented as a string    
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

    try:
        content_type = grid_out.metadata['content_type']
    except KeyError:
        content_type = 'audio/mpeg' # probably a sane guess

    async def reader():
        while grid_out.tell() < grid_out.length:
            yield await grid_out.readchunk()
    
    return StreamingResponse(reader(), media_type=content_type, headers={
        'Content-Disposition': f'attachment; filename="{grid_out.filename}"',
        'Cache-Control': 'public, max-age=31536000, immutable, no-transform',
        'Content-Length': str(grid_out.length)
    })