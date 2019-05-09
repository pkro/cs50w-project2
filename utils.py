import time
import sys
from datetime import datetime

import config

def cachebuster():
    return time.time() if config.debug else "static"

def get_timestamp():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def dbg(text):
    print(text, file=sys.stdout)