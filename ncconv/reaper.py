# Copyright (C) 2022  Aurora McGinnis
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation using version 3 of the License ONLY.
#
# See LICENSE.txt for more information.
#
# reaper.py - Contains logic for the reaper thread, which is responsible for
# freeing unused MongoDB objects in the background.


from more_itertools import chunked
from queue import Empty, Queue
from contextlib import suppress

import sentry_sdk

from ncconv.config import SENTRY_DSN


# collection to aggregate on / delete from, pipeline
__pipelines = [
    (
        'music.files',
        [
            {
                '$lookup': {
                    'from': 'queue',
                    'localField': '_id',
                    'foreignField': 'pending_file',
                    'as': 'referenced_by'
                }
            }, {
                '$match': {
                    'referenced_by': {
                        '$size': 0
                    },
                    'metadata.pending': True
                }
            }, {
                '$project': {
                    '_id': 1
                }
            }
        ]
    ),
    (
        'music.chunks',
        [
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
        ]
    )
]


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
            for collection, pipeline in __pipelines:
                cur = db[collection].aggregate(pipeline)

                for docs in chunked(cur, 50):
                    db[collection].delete_many({
                        '$or': [{'_id': doc['_id']} for doc in docs]
                    })

        except Exception as e:
            if SENTRY_DSN:
                sentry_sdk.capture_exception(e)

            print(e)
