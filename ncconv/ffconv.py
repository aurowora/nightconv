# Copyright (C) 2022  Aurora McGinnis
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation using version 3 of the License ONLY.
#
# See LICENSE.txt for more information.
#
# ffconv.py - Functions that handle interaction with ffmpeg / ffprobe.


import subprocess
from typing import Tuple
from tempfile import TemporaryDirectory
import os

from fastapi import HTTPException
from orjson import loads as json_loads

from ncconv.config import FFMPEG_EXEC, FFPROBE_EXEC, DEFAULT_PITCH, DEFAULT_TEMPO, MAX_ARTIFACT_SIZE


def _probe_audio(input_stream: bytes) -> Tuple[str, int]:
    '''
    Guess the input format and sample rate based on the buffer. Raise an exception if we don't know!

    :param input_stream: Audio stream to guess the type of
    '''

    proc = subprocess.run((FFPROBE_EXEC, '-v', 'quiet', '-print_format', 'json', '-show_format', '-show_streams', '-'), capture_output=True, input=input_stream)
    format_info = json_loads(proc.stdout)

    if 'format' not in format_info or 'streams' not in format_info or format_info['format']['format_name'] not in ('ogg', 'oga', 'opus', 'mp3', 'flac', 'wav'):
        print(format_info)
        raise HTTPException(status_code=400, detail='Unsupported input format')

    # This is needed because we need to specify input format in convert_audio
    format = format_info['format']['format_name']

    # We need the sample rate because we need to calculate the new rate based on this sample rate
    for stream in format_info['streams']:
        if stream['codec_type'] == 'audio':
            sample_rate = int(stream['sample_rate'])
            break
    else:
        raise HTTPException(status_code=400, detail='Could not find stream in input file')

    return format, sample_rate


def _construct_filters(tempo_scaler: float, orig_sample_rate: int, new_sample_rate: int) -> str:
    '''
    Constructs the filters to be passed to ffmpeg.

    Raises an exception for invalid input

    :param tempo_scaler: Percent by which to change the tempo as a fraction of 1
    :param orig_sample_rate: Source sample rate
    :param new_sample_rate: Adjusted sample rate
    '''
    filters = []

    # ffmpeg kinda messes it up when we have tempo scalers that scales the tempo by a factor of 2 or more
    # to resolve this, we can pass multiple atempo filters.
    # This loop computes the lowest root of tempo_scaler that is less than or equal to t. We'll pass n filters with value r
    if tempo_scaler > 2 or tempo_scaler < 0.5:
        t = 0.5 if tempo_scaler < 0.5 else 2

        for n in range(2, 10):
            if (r := tempo_scaler ** (1/n)) <= t:
                break
        else:
            raise HTTPException(status_code=400, detail='Tempo scale factor is too large.')
        
        for _ in range(n):
            filters.append(f'atempo={r:.4f}')
    else:
        filters.append(f'atempo={tempo_scaler:.3f}')

    return ','.join((*filters, f'asetrate={new_sample_rate}', f'aresample={orig_sample_rate}'))


# converts the output_format string to the ffmpeg params
# input -> (format, codec)
__ffmpeg_formats = {
    'm4a': ('mp4', 'aac'),
    'ogg': ('ogg', 'libvorbis')
}    

def convert_audio(input_stream: bytes, output_format: str = 'm4a', tempo_scaler: float = DEFAULT_TEMPO, pitch_scaler: float = DEFAULT_PITCH) -> bytes:
    '''
    Perform the conversion and returns the result.

    This routine blocks and shouldn't be called on the main thread.
    
    :param input_stream: Audio stream to convert
    :param output_format: One of m4a or ogg
    :param tempo_scaler: Percent by which to change the tempo as a fraction of 1
    :param pitch_scaler: Percent by which to change the pitch as a fraction of 1
    '''

    input_format, orig_sample_rate = _probe_audio(input_stream)
    sample_rate = orig_sample_rate * pitch_scaler
    filters = _construct_filters(tempo_scaler, orig_sample_rate, sample_rate)
    try:
        output_format, output_codec = __ffmpeg_formats[output_format]
    except KeyError:
        raise HTTPException(status_code=400, detail='Unsupported output format')

    # We can't just read stdout because the mp4 muxer doesn't support non-seekable outputs
    with TemporaryDirectory() as td:
        tfp = os.path.join(td, 'output')
        # Perform the conversion! Wow!
        proc = subprocess.run((FFMPEG_EXEC, '-i', 'pipe:', '-f', input_format, '-c:a', output_codec, '-vn', '-f', output_format, '-af', filters, tfp), input=input_stream, capture_output=True)

        if proc.returncode != 0:
            print(proc.stderr)
            raise HTTPException(status_code=500, detail='Audio conversion failed')

        if os.stat(tfp).st_size > MAX_ARTIFACT_SIZE:
            raise HTTPException(status_code=400, detail='Resulting file exceeded the size limit.')

        with open(tfp, 'rb') as fp:
            return fp.read()
