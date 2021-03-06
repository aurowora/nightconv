# Copyright (C) 2022  Aurora McGinnis
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation using version 3 of the License ONLY.
#
# See LICENSE.txt for more information.
#
# config.py - Reads configuration from file for importing by other modules.


from starlette.config import Config
from starlette.datastructures import CommaSeparatedStrings
from multiprocessing import cpu_count
import os

config_file = '.env' if 'NCCONV_CONF' not in os.environ else os.environ['NCCONV_CONF']
config = Config(config_file)

# Connection URI for MongoDB
MONGO_URI = config('MONGO_URI')
# Mongo database to use
MONGO_DB = config('MONGO_DB', default='ncconv')
# FFMPEG binaries to use
FFMPEG_EXEC = config('FFMPEG_BIN', default='ffmpeg')
FFPROBE_EXEC = config('FFPROBE_BIN', default='ffprobe')
# Allowed hosts
HOSTS = config('TRUSTED_HOSTS', cast=CommaSeparatedStrings,
               default=CommaSeparatedStrings('127.0.0.1, localhost'))
# Allowed hosts for CORS
CORS_HOSTS = config('TRUSTED_CORS_HOSTS', cast=CommaSeparatedStrings,
                    default=CommaSeparatedStrings('http://127.0.0.1:8080, http://localhost:8080'))
# Used for determining the real ip address of the client
TRUSTED_PROXIES = config('TRUSTED_PROXIES', cast=CommaSeparatedStrings,
                         default=CommaSeparatedStrings('127.0.0.1'))
# IP and port to bind
BIND_HTTP_IP = config('HTTP_IP', default='127.0.0.1')
BIND_HTTP_PORT = config('HTTP_PORT', cast=int, default=8080)
# How many threads to spawn for serving requests
HTTP_WORKERS = config('HTTP_WORKERS', cast=int, default=cpu_count())
# How many threads to spawn for converting files
FFMPEG_WORKERS = config('FFMPEG_WORKERS', cast=int, default=cpu_count())
# If using sentry, specify DSN here
SENTRY_DSN = config('SENTRY_DSN', default=None)
# refuse to store files larger than this
MAX_ARTIFACT_SIZE = config(
    'MAX_ARTIFACT_SIZE', cast=int, default=(20 * (1024 ** 2)))

# Not a configuration option, but it lives here because I said so :)
VERSION = '0.1-ALPHA'
DEFAULT_PITCH = 1.25
DEFAULT_TEMPO = 1.10
