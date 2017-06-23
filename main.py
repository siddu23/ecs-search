"""Search Microservice v1.0
Primary gateway to search data from pratilipi data store
currently supports search of -
- authors
- pratilipis (content)
"""

import os
import sys
import requests
import inspect
import simplejson as json
import bottle
import time
from datetime import datetime
from bottle import Bottle, route, run, request, response
application = Bottle()

# set the base path
sys.path.append("%s/src" % os.getcwd())
sys.path.append("%s/lib" % os.getcwd())
sys.path.append("%s/config" % os.getcwd())

import v1
from commonfns import api_response, log_formatter, requested_api_version
import config

print log_formatter(inspect.stack()[0][3], os.environ)

#fetch config
config_dict = {'solr_url': config.SOLR_URL,
               'pratilipi_url': config.PRATILIPI_SERVICE_URL,
               'author_url': config.AUTHOR_SERVICE_URL,
               'trending_limit': config.TOP_SEARCH_LIMIT,
               'trending_age': config.TOP_SEARCH_AGE_IN_MIN,
               'redis_url': config.REDIS_URL,
               'redis_port': config.REDIS_PORT,
               'redis_db': config.REDIS_DB,}
print log_formatter(inspect.stack()[0][3], config_dict)


def timeit(method):
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()

        ft = "timetaken - {0:.2f} sec".format(te-ts)
        print log_formatter(method.__name__, ft)
        return result
    return timed


@application.hook('after_request')
def enable_cors():
    response.set_header('Access-Control-Allow-Origin', '*')
    response.set_header('Access-Control-Allow-Credentials', 'true')
    response.set_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
    response.set_header('Access-Control-Allow-Headers', 'AccessToken, Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token, Version')


@application.route('/health', method=['OPTIONS', 'GET'])
@application.route('/search/health', method=['OPTIONS', 'GET'])
def health():
    """
    health - to check health of the api
    """

    #print log_formatter(inspect.stack()[0][3], "health check - OK")
    result = [200, "OK", {"state":"healthy"}]
    return api_response(result)


@application.route('/search/search', method=['OPTIONS', 'GET'])
@timeit
def search():
    """
    search data
    """
    st = time.time()
    # set default response
    result = [404, "Not Found"]

    if request.method == "OPTIONS":
        return api_response([200, "Success"])
    elif request.method != "GET":
        return api_response(result)

    print log_formatter(inspect.stack()[0][3], "search start")
    
    user_id = request.headers.get('User-Id', 0)

    if requested_api_version(request.headers) == 1.0:
        result = v1.search(config_dict, request.query, user_id)

    print log_formatter(inspect.stack()[0][3], "search done")
    return api_response(result)


@application.route('/search/trending_search', method=['OPTIONS', 'GET'])
@timeit
def trending_search():
    """
    trending search
    """
    # set default response
    result = [404, "Not Found"]

    if request.method == "OPTIONS":
        return api_response([200, "Success"])
    elif request.method != "GET":
        return api_response(result)

    print log_formatter(inspect.stack()[0][3], "trending search start")

    if requested_api_version(request.headers) == 1.0:
        result = v1.trending_search(config_dict, request.query)

    print log_formatter(inspect.stack()[0][3], "trending search done")
    return api_response(result)


if __name__ == '__main__':
    print log_formatter(inspect.stack()[0][3], "start running search app")
    run(application, host='127.0.0.1', port=8080)


