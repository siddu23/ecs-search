import re
import os

from datetime import datetime

def requested_api_version(data):
    accepttxt = data.get('Accept', "Version=1.0")
    searchtxt = re.search(r'Version=(\d.\d)', accepttxt.lower())
    version = 1.0
    accepttxt = data.get('Accept', "Version=1.0")
    if searchtxt:
        version = searchtxt.group()[-3:]
    return version


def api_response(result):
    """
    api response formatter
    """
    """
    response = {}
    response["response_header"] = {"status_code": result[0], "msg": result[1]}
    if len(result) > 2 and result[2] != {}:
        response["response"] = result[2]
    return response
    """
    response = {}
    if result[0] != 200:
        response = {"message": result[1]}
    else:
        if len(result) > 2:
            response = result[2]
    return response


def log_formatter(fname, msg, level="INFO"):
    hostname = os.uname()[1]
    pid = os.getpid()
    return "[%s] [%s] [%s] [%s] [%s] - %s" % (datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"), hostname, pid, level, fname, msg)



