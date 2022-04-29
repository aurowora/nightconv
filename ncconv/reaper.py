import time

from more_itertools import chunked
from queue import Empty, Queue
from contextlib import suppress

import sentry_sdk

from ncconv.config import SENTRY_DSN


def reaper_task(q: Queue, db):
    '''
    Thread periodically frees orphaned gridfs chunks when the parent is killed by the database
    '''

    while True:
        try:
            with suppress(Empty):
                poison = q.get(block=True, timeout=30)
                if poison:
                    break

            # Fetch a cursor of documents to delete
            cur = db.music.chunks.aggregate([
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

            for docs in chunked(cur, 50):
                db.music.chunks.delete_many({
                        '$or': [{'_id': doc['_id']} for doc in docs]
                })

        except Exception as e:
            if SENTRY_DSN:
                sentry_sdk.capture_exception(e)

            print(e)
