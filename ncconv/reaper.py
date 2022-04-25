from asyncio import sleep
from random import randint
from contextlib import suppress

from fastapi import FastAPI
from more_itertools import chunked
import sentry_sdk

from ncconv.config import SENTRY_DSN


async def reaper_task(app: FastAPI):
    '''
    Periodically frees orphaned gridfs chunks when the parent is killed by the database

    Does not return. Use crate_task() with this.
    '''

    while True:
        try:
            # add a bit of jitter because there's going to be as many reapers as we have cores by default
            await sleep(1800 + randint(0, 3600))

            # Fetch a cursor of documents to delete
            cur = await app.state.db.music.chunks.aggregate([
                {
                    '$lookup': {
                        'from': 'music.files',
                        'localField': 'files_id',
                        'foreignField': '_id',
                        'as': 'referenced_by'
                    }
                }, {
                    '$match': {
                        'referenced_by': {
                            '$size': 0
                        }
                    }
                }, {
                    '$project': {
                        '_id': 1
                    }
                }
            ])

            # each() doesn't seem to be supported with asyncio?
            async for docs in chunked(cur, 50):
                await app.state.db.music.chunks.delete_many({
                    '$or': docs
                })
        except Exception as e:
            if SENTRY_DSN:
                sentry_sdk.capture_exception(e)

            print(e)
