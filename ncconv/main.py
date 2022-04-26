#! /usr/bin/env python3

from asyncio import get_running_loop
from threading import Thread
from queue import Queue
import shutil, sys

from fastapi import FastAPI, HTTPException
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware
from fastapi.middleware.cors import CORSMiddleware
from uvicorn import run
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorGridFSBucket
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware
from sentry_sdk import init as sentry_init
from pymongo import MongoClient

from ncconv.config import FFMPEG_EXEC, FFPROBE_EXEC, MONGO_URI, BIND_HTTP_PORT, BIND_HTTP_IP, HOSTS, TRUSTED_PROXIES, HTTP_WORKERS, MONGO_DB, CORS_HOSTS, VERSION, SENTRY_DSN
from ncconv.cworkers import fftask
from ncconv.reaper import reaper_task
from ncconv.routes.media import media_router
from ncconv.routes.convert import convert_router


app = FastAPI(docs_url = None, redoc_url = None)

# Add the desired middleware
app.add_middleware(GZipMiddleware)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=HOSTS)
app.add_middleware(ProxyHeadersMiddleware, trusted_hosts=TRUSTED_PROXIES) # This is important so that our rate limiting hits actual client IP addresses
app.add_middleware(CORSMiddleware, allow_origins=CORS_HOSTS, allow_methods=['GET', 'POST'], allow_headers=['Content-Length'], max_age=3600, expose_headers=['Retry-After'])

# sentry support
if SENTRY_DSN:
    def ignore_user_errors(event, hint):
        if 'exc_info' in hint:
            ty, val, _ = hint['exc_info']

            if isinstance(ty, HTTPException):
                if 400 <= val.status_code < 500:  # ignore anything caused by the user
                    return None
        
        return event

    sentry_init(dsn=SENTRY_DSN, release=VERSION, before_send=ignore_user_errors)

    app.add_middleware(SentryAsgiMiddleware)


# Add subrouters
app.include_router(media_router)
app.include_router(convert_router)


@app.on_event('startup')
async def initialize():
    # Connect to the database
    app.state.db = AsyncIOMotorClient(MONGO_URI)[MONGO_DB]
    app.state.file_store = AsyncIOMotorGridFSBucket(app.state.db, bucket_name="music")

    # Setup indexes

    # This will destroy the file (and link) but not free the storage!
    # The reaper will clean up orphaned chunks later
    await app.state.db.music.files.create_index([("metadata.expire_time", 1)], expireAfterSeconds=0)
    await app.state.db.queue.create_index([('expire_time', 1)], expireAfterSeconds=0)

    # Rate limits
    await app.state.db.ratelimits.create_index([('bucket_expires', 1)], expireAfterSeconds=0)
    await app.state.db.ratelimits.create_index([('ip', 1), ('key', 1)], unique=True)

if __name__ == '__main__':
    # check that ffmpeg is present
    if not shutil.which(FFMPEG_EXEC) or not shutil.which(FFPROBE_EXEC):
        print('FATAL: ffmpeg or ffprobe was not found in PATH. Install them and try again.')
        sys.exit(1)
    
    # Create threads for ffmpeg
    # sync db handle
    db = MongoClient(MONGO_URI)[MONGO_DB]

    q = Queue()
    ffthread = Thread(target=fftask, args=(q, db), name='orchestrator-thread').start()

    reaper_thread = Thread(target=reaper_task, args=(q, db), name='reaper-thread').start()

    run('ncconv.main:app', host=BIND_HTTP_IP, port=BIND_HTTP_PORT, log_level='info', workers=HTTP_WORKERS)
    
    for x in range(2):
        q.put(1)  # Tell our threads to terminate
    
    print('Waiting for all threads to terminate.')