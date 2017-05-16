from datetime import datetime

def api_response(status_code, msg, data=None):
    """
    api response formatter
    """
    response = {}
    response["response_header"] = {"status_code": status_code, "msg": msg}
    if data is not None:
        response["response"] = data
    return response

def log_formatter(fname, msg):
    return "[%s] %s, %s" % (datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"), fname, msg) 

