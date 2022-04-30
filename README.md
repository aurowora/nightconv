# Nightconv

A simple website written using FastAPI and Svelte to convert audio files into [Nightcore](https://en.wikipedia.org/wiki/Nightcore).

![Screenshot of Nightconv](/.github/img1.jpg)

### Building

To compile the front end, simply run make with NodeJS and NPM installed:

```shell
make
```

This will compile the Svelte app and copy the `public` directory into the current folder so that it may be served by the application.

### Configuration

The application can be configured by creating a file called `.env` in the working directory of the Python process. The file can also be read from elsewhere if the `NCCONV_CONF` environment variable has been set.

Inside this file, insert lines of form `KEY=VALUE`. The following configuration options are available:

| Key | Default | Description |
|-----|---------|-------------|
|MONGO_URI|No Default|The URI to use to connect to MongoDB. Required.|
|MONGO_DB|ncconv|The name of the MongoDB database to use.|
|FFMPEG_BIN|ffmpeg|The path to the ffmpeg binary. Required if `ffmpeg` is not in the `$PATH`.|
|FFPROBE_BIN|ffprobe|Same as above, but for `ffprobe`.|
|TRUSTED_HOSTS|127.0.0.1,localhost|List of domain names that this application is to be accessed from. Multiple can be specified by placing a comma between values (`value1,value2`). Required if not running on `127.0.0.1`.|
|TRUSTED_CORS_HOSTS|`127.0.0.1`|List of domain names that are allowed to use the API from a web browser. Required if not running on `127.0.0.1`.|
|TRUSTED_PROXIES|`127.0.0.1`|List of trusted proxy IP addresses. Required if running behind a proxy such as NGINX or Cloudflare (which is recommended!)|
|BIND_HTTP_IP|`127.0.0.1`|The IP to bind to. The default value is recommended almost always. If you wish to expose the application publicly, then use a reverse proxy that supports TLS like NGINX.|
|BIND_HTTP_PORT|8080|HTTP port to listen on.|
|HTTP_WORKERS|# of CPUs|The number of processes to spawn for handling HTTP requests.|
|FFMPEG_WORKERS|# of CPUs|The number of threads available for converting media files.|
|SENTRY_DSN|None|Enables error reporting to Sentry.|
|MAX_ARTIFACT_SIZE|20971520|The system will refuse to store any media file longer than this many bytes. Default is 20 MiB.

#### Further Notes Regarding Configuration

- This application should be ran behind a reverse proxy rather than being directly exposed to the internet. Reverse proxies support nice things like TLS.
- If the service is accessible from the internet, then a maximum upload size should be configured on the reverse proxy. Otherwise users could submit audio files of arbritrary size, which can easily consume large amounts of memory.
- Audio files are stored in MongoDB using GridFS. Your database server should have sufficient storage to store these objects.
- It is safe to run multiple instances of the application against the same database.

### Installing & Running

(Be sure that you've built the front-end as in *Building* before running the application.)

Running the application requires that python3, ffmpeg, ffprobe are all installed and available in the `$PATH`. Additionally, pip and virtual environment support must be present as well.

Start by initializing a virtual environment and installing the necessary dependencies:

```shell
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Then, run the main module:

```shell
python3 -m ncconv.main
```

You can configure the application to start on boot using your system's init daemon.

On Linux with systemd, create a new unit file at `/etc/systemd/system/ncconv.service` with the following contents:

```
[Unit]
Description = Nightconv Application Server

[Service]
Type=simple
ExecStart=/bin/sh -c 'source .venv/bin/activate && python3 -m ncconv.main'
WorkingDirectory=/path/to/this/repos/root/
User=nobody
Group=nogroup  # You may have to adjust the group names depending on your distro

[Install]
WantedBy=multi-user.target
```

Then, simply enable and start:

```shell
systemctl enable --now ncconv.service
```

### License

Copyright (C) 2022  Aurora McGinnis

This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License ONLY.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License along with this program.  If not, see <https://www.gnu.org/licenses/>.