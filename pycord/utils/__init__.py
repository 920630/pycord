"""
MIT License

Copyright (c) 2017 verixx / king1600

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import os
import re
import time
from base64 import b64encode
from datetime import datetime, timedelta

from multio import asynclib

from .collection import Collection
from .emitter import Emitter
from .commands import *
from .converter import *

# get the library name by folder
def get_libname():
    return __file__.split(os.sep)[-3]

# PARSING
import json
encoder = json.dumps
decoder = json.loads
encoding = "json"


# api constants
class API:
    HOST = "https://discordapp.com"
    HTTP_ENDPOINT = "{}/api/v7".format(HOST)
    WS_ENDPOINT = "?v=7&encoding={}".format(encoding)


# Time Functions

DISCORD_EPOCH = 1420070400000


def parse_time(timestamp):
    if timestamp:
        return datetime(*map(int, re.split(r'[^\d]', timestamp.replace('+00:00', ''))))
    return None


def gt(dt_str):
    dt, _, us = dt_str.partition(".")
    dt = datetime.strptime(dt, "%Y-%m-%dT%H:%M:%S")
    us = int(us.rstrip("Z"), 10)
    return dt + timedelta(microseconds=us)


def id_to_time(id):
    return datetime.utcfromtimestamp(
        ((int(id) >> 22) + DISCORD_EPOCH) / 1000
    )


def time_to_id(timeobj, high=False):
    secs = (timeobj - type(timeobj)(1970, 1, 1).total_seconds())
    discord_ms = int(secs * 1000 - DISCORD_EPOCH)
    return (discord_ms << 22) + ((1 << 22) - 1 if high else 0)


def id_now():
    secs = time.time()
    discord_ms = int(secs * 1000 - DISCORD_EPOCH)
    return discord_ms << 22


#  Data formatting

def image_type(data):
    if data.startswith(b'\x89\x50\x4E\x47\x0D\x0A\x1A\x0A'):
        return 'image/png'
    elif data.startswith(b'\xFF\xD8') and data.endswith(b'\xFF\xD9'):
        return 'image/jpeg'
    else:
        raise ValueError('Unsupported image type')


def image_to_string(data):
    mime = image_type(data)
    data = b64encode(data).decode('ascii')
    return 'data:{0},base64,{1}'.format(mime, data)


async def run_later(time, task):
    await asynclib.sleep(time)
    return await task
