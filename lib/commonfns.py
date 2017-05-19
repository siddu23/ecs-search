import ConfigParser
import re

from datetime import datetime


def requested_api_version(data):
    accepttxt = data.get('Accept', "version=1.0")
    searchtxt = re.search(r'version=(\d.\d)', accepttxt.lower())
    version = 1.0
    accepttxt = data.get('Accept', "version=1.0")
    if searchtxt:
        version = searchtxt.group()[-3:]
    return version


def api_response(result):
    """
    api response formatter
    """
    response = {}
    response["response_header"] = {"status_code": result[0], "msg": result[1]}
    if len(result) > 2 and result[2] != {}:
        response["response"] = result[2]
    return response


def log_formatter(fname, msg):
    return "[%s] %s, %s" % (datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"), fname, msg)


def config_builder(base_path):
    config_path = "%s/%s" % (base_path.replace('src', 'config'), "search.cnf")
    search_config = ConfigParser.RawConfigParser()
    search_config.read(config_path)
    config_dict = {'solr_url': search_config.get("SOLR", "BASE_URL"),
                  'pratilipi_url': search_config.get("PRATILIPI_SERVICE", "BASE_URL"),
                  'author_url': search_config.get("AUTHOR_SERVICE", "BASE_URL"),
                  'log_user_activity': bigquery_ops.connect_gcloud("search", "user_activity"),
                  'trending_limit': search_config.get("TOP_SEARCH", "LIMIT"),
                  'trending_age': search_config.get("TOP_SEARCH", "AGE_IN_MIN")}
    return config_dict


