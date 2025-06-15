from bson import json_util
import logging
from logging import Formatter
from logging.handlers import RotatingFileHandler
from datetime import datetime
import time

class JsonFormatter(Formatter):
    def __init__(self):
        super(JsonFormatter, self).__init__()

    def format(self, record):
        #print(json_util.dumps(record.__dict__, indent=4))
        json_record = {
            "timestamp": datetime.fromtimestamp(time.time()).isoformat(),
            "message": record.getMessage(),
            "name": record.__dict__['name'],
            "msecs": record.__dict__['msecs'],
            "module": record.__dict__['module'],
            "function": record.__dict__['funcName']
        }

        extra_fields = record.__dict__.get('extra_fields', {})
        for field in extra_fields:
            json_record[field] = extra_fields[field]
        if record.levelno == logging.ERROR and record.exc_info:
            json_record["err"] = self.formatException(record.exc_info)
        return json_util.dumps(json_record)

logger = logging.root

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(JsonFormatter())

file_handler = RotatingFileHandler('/tmp/main.log', maxBytes=5e6, backupCount=10)
file_handler.setFormatter(JsonFormatter())

logger.handlers = [stream_handler, file_handler]
logger.setLevel(logging.INFO)
logging.getLogger("uvicorn.access").disabled = True
