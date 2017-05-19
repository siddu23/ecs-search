"""Search Microservice v1.0
Primary gateway to search data from pratilipi data store
currently supports search of -
- authors
- pratilipis (content)
"""

import os
import sys
import argparse
import requests
import inspect
import simplejson as json
import threading

from datetime import datetime
from bottle import route, run, request, response

# set the base path
sys.path.append("%s/lib" % os.getcwd())
BASE_PATH = os.path.abspath(os.path.dirname(__file__))

import v1
import bigquery_ops
from commonfns import api_response, log_formatter

# fetch config
CONFIG_DICT = config_builder(BASE_PATH)


@route('/ping')
def ping():
    """
    ping - to check if the api is up
    """

    print log_formatter(inspect.stack()[0][3], "pong")
    result = [200, "OK"]
    return api_response(result)


@route('/search')
def search():
    """
    search data
    """
    print log_formatter(inspect.stack()[0][3], "search start")

    result = [404, "Not Found"]

    if requested_api_version(request.headers) == 1.0:
        result = v1.search(CONFIG_DICT, request.query)

    print log_formatter(inspect.stack()[0][3], "search done")

    return api_response(result)


@route('/trending_search')
def trending_search():
    """
    trending search
    """
    print log_formatter(inspect.stack()[0][3], "trending search start")

    result = [404, "Not Found"]

    if requested_api_version(request.headers) == 1.0:
        result = v1.trending_search(CONFIG_DICT, request.query)

    print log_formatter(inspect.stack()[0][3], "trending search done")

    return api_response(result)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("host", type=str, help="host")
    parser.add_argument("port", type=int, help="port")
    args = parser.parse_args()

    run(host=args.host, port=args.port)


