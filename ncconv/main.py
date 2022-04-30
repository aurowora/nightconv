#! /usr/bin/env python3
# Copyright (C) 2022  Aurora McGinnis
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation using version 3 of the License ONLY.
#
# See LICENSE.txt for more information.
#
# ncconv / nightconv - A webservice for converting audio files to nightcore.


from threading import Thread
from queue import Queue
import shutil
import sys

from fastapi import FastAPI, HTTPException
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from uvicorn import run
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorGridFSBucket
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware
from sentry_sdk import init as sentry_init
from pymongo import MongoClient
from brotli_asgi import BrotliMiddleware

from ncconv.config import FFMPEG_EXEC, FFPROBE_EXEC, MONGO_URI, BIND_HTTP_PORT, BIND_HTTP_IP, HOSTS, TRUSTED_PROXIES, HTTP_WORKERS, MONGO_DB, CORS_HOSTS, VERSION, SENTRY_DSN
from ncconv.cworkers import fftask
from ncconv.reaper import reaper_task
from ncconv.routes.media import media_router
from ncconv.routes.convert import convert_router


api = FastAPI(docs_url=None, redoc_url=None)

# Add the desired middleware
api.add_middleware(TrustedHostMiddleware, allowed_hosts=HOSTS)
# This is important so that our rate limiting hits actual client IP addresses
api.add_middleware(ProxyHeadersMiddleware, trusted_hosts=TRUSTED_PROXIES)
api.add_middleware(CORSMiddleware, allow_origins=CORS_HOSTS, allow_methods=[
                   'GET', 'POST'], allow_headers=['Content-Length'], max_age=3600, expose_headers=['Retry-After'])
api.add_middleware(BrotliMiddleware, gzip_fallback=True, minimum_size=400)

# Add subrouters
api.include_router(media_router)
api.include_router(convert_router)


# Serve the web app
sf = BrotliMiddleware(StaticFiles(directory='public',
                      html=True), gzip_fallback=True)

# Configure a wrapper FastAPI app

app = FastAPI(docs_url=None, redoc_url=None)
app.mount('/api', api)
app.mount('/', sf, name='static')

# sentry support
if SENTRY_DSN:
    def ignore_user_errors(event, hint):
        if 'exc_info' in hint:
            ty, val, _ = hint['exc_info']

            if isinstance(ty, HTTPException):
                if 400 <= val.status_code < 500:  # ignore anything caused by the user
                    return None

        return event

    sentry_init(dsn=SENTRY_DSN, release=VERSION,
                before_send=ignore_user_errors)

    app.add_middleware(SentryAsgiMiddleware)


# Events do not get called for mounted apps
@app.on_event('startup')
async def initialize():
    # Connect to the database
    api.state.db = AsyncIOMotorClient(MONGO_URI)[MONGO_DB]
    api.state.file_store = AsyncIOMotorGridFSBucket(
        api.state.db, bucket_name="music")

    # Setup indexes

    # This will destroy the file (and link) but not free the storage!
    # The reaper will clean up orphaned chunks later
    await api.state.db.music.files.create_index([("metadata.expire_time", 1)], expireAfterSeconds=0)
    await api.state.db.queue.create_index([('expire_time', 1)], expireAfterSeconds=0)

    # If the client does not check the status of the queued item within 30 seconds
    # we assume they've lost interest and delete the item (navigated away, etc)
    await api.state.db.queue.create_index([('last_checked', -1)], expireAfterSeconds=30)

    # Rate limits
    await api.state.db.ratelimits.create_index([('bucket_expires', 1)], expireAfterSeconds=0)
    await api.state.db.ratelimits.create_index([('ip', 1), ('key', 1)], unique=True)


if __name__ == '__main__':
    # check that ffmpeg is present
    if not shutil.which(FFMPEG_EXEC) or not shutil.which(FFPROBE_EXEC):
        print('FATAL: ffmpeg or ffprobe was not found in PATH. Install them and try again.')
        sys.exit(1)

    # Create threads for ffmpeg
    # sync db handle
    db = MongoClient(MONGO_URI)[MONGO_DB]

    q = Queue()
    ffthread = Thread(target=fftask, args=(q, db), name='fftask-0').start()

    reaper_thread = Thread(target=reaper_task, args=(
        q, db), name='reaper-task').start()

    run('ncconv.main:app', host=BIND_HTTP_IP, port=BIND_HTTP_PORT,
        log_level='info', workers=HTTP_WORKERS)

    for x in range(2):
        q.put(1)  # Tell our threads to terminate

    print('Waiting for all threads to terminate.')
