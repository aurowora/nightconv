from contextlib import suppress
from datetime import datetime, timedelta, timezone
from os import path
from queue import Empty, Queue
import re
from threading import Thread
from time import sleep
from fastapi import HTTPException

from pymongo import MongoClient
import gridfs
import sentry_sdk

from ncconv.config import MONGO_URI, MONGO_DB, FFMPEG_WORKERS, SENTRY_DSN
from ncconv.ffconv import convert_audio

def fftask(q: Queue):
    '''
    This thread spawns FFMPEG_WORKER threads to handle conversion jobs.
    Once threads are spawned, it waits for incoming requests and dispatches them to workers as needed.

    Sending any value but None on q will cause the thread to terminate child threads and die

    :param q: Termination signal queue
    '''

    db = MongoClient(MONGO_URI)[MONGO_DB]
    wq = Queue()

    my_threads = [Thread(target=_ffworker, args=(wq, db), daemon=True) for i in range(FFMPEG_WORKERS)]

    for t in my_threads:
         t.start()

    while True:
        try:
            with suppress(Empty):
                poison = q.get_nowait()
                if poison:
                    break
            
            # this is an atomic operation with respect to the doc
            doc = db.queue.find_one_and_update(
                {'state': 0},
                {'$inc': {'state': 1}},
                sort=[('_id', 1)]
            )

            if doc:
                wq.put(doc, block=True)
            else:
                sleep(5)
        except Exception as e:
            if SENTRY_DSN:
                sentry_sdk.capture_exception(e)

            print(e)

    for t in range(FFMPEG_WORKERS):
        wq.put(1, block=True)

    for t in my_threads:
        t.join()


def _ffworker(q: Queue, db):
    '''
    FFmpeg worker thread. Spawned by fftask. Listens on q for jobs, performs the job, and updates the db record with the result

    :param q: Job queue
    :param db: Database reference
    '''

    g = gridfs.GridFS(db, collection='music')

    while (doc := q.get(block=True)) != 1:
        try:
            try:
                pending_file, scale_pitch, scale_tempo, output_format = doc['pending_file'], doc['scale_pitch'], doc['scale_tempo'], doc['output_format']
                f = g.find_one(pending_file)

                if not f:
                    raise HTTPException(status_code=404, detail='No such pending file')
                
                # rename and escape the filename
                fn = re.sub(r'(?u)[^-\w.]', '', f.filename.strip().replace(' ', '_'))
                fn = path.splitext(fn)[0] + '.night' + ('.mp3' if output_format == 'mp3' else '.opus')

                # Perform the conversion and upload it
                buf = convert_audio(f.read(), output_format, scale_tempo, scale_pitch)
                inserted_id = g.put(buf, metadata = {
                    'content_type': 'audio/mpeg' if output_format == 'mp3' else 'audio/ogg',
                    'expire_time': datetime.now(timezone.utc) + timedelta(days=1),
                    'uploaded_by': str(doc['enqueued_by'])
                }, filename=fn)

                # update the database document so that a client calling /check can see the new file
                db.queue.replace_one({'_id': doc['_id']}, {
                    '_id': doc['_id'],
                    'state': 2,
                    'completed_file': inserted_id,
                    'expire_time': doc['expire_time']

                })                
            except (HTTPException, Exception) as e:
                if isinstance(e, HTTPException):
                    status_code, detail = e.status_code, e.detail
                else:
                    status_code, detail = 500, "An unexpected error occurred during the conversion of your file. Try again!"

                db.queue.replace_one({'_id': doc['_id']}, {
                    'state': 3,
                    'status_code': status_code,
                    'detail': detail,
                    'expire_time': doc['expire_time']
                })

                raise e
            finally:
                with suppress(Exception):
                    g.delete(pending_file)
        except Exception as e:
            if SENTRY_DSN:
                sentry_sdk.capture_exception(e)
            
            print(e)