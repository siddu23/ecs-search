"""Search Microservice v1.0
Primary gateway to get data from pratilipi data store
currently supports search of -
- authors
- pratilipis (content)
"""

import os
import sys
import argparse
import ConfigParser
import requests
import inspect
import simplejson as json
import re

from datetime import datetime
from bottle import route, run, request, response, template

# set the base path
sys.path.append("%s/lib" % os.getcwd())
BASE_PATH = os.path.abspath(os.path.dirname(__file__))

from bigquery_ops import stream_data
from commonfns import api_response, log_formatter


# fetch config
CONFIG_PATH = "%s/%s" % (BASE_PATH.replace('src', 'config'), "search.cnf")
SEARCH_CONFIG = ConfigParser.RawConfigParser()
SEARCH_CONFIG.read(CONFIG_PATH)
SOLR_URL = SEARCH_CONFIG.get("SOLR", "BASE_URL")
PRATILIPI_URL = SEARCH_CONFIG.get("PRATILIPI_SERVICE", "BASE_URL")
AUTHOR_URL = SEARCH_CONFIG.get("AUTHOR_SERVICE", "BASE_URL")


@route('/ping')
def ping():
    """
    ping - to check if the api is up
    """
    return log_formatter(inspect.stack()[0][3], "pong")


@route('/searchx')
def searchx():
    """
    search for internal usage, dosen't call any external service
    """
    print log_formatter(inspect.stack()[0][3], "search start")

    accepttxt = request.headers.get('Accept', "version=1.0")
    searchtxt = re.search(r'version=(\d.\d)', accepttxt.lower())
    version = 1.0
    if searchtxt:
        version = searchtxt.group()[-3:]

    userid = request.query.get('userid', None)
    text = request.query.get('text', None)
    lang = request.query.get('lang', None)
    platform = request.query.get('platform', 'web')
    is_active = request.query.get('is_active', True)
    limit = request.query.get('limit', 20)
    offset = request.query.get('offset', 0)

    if text is None:
        return api_response(400, "Bad Request")

    log_data = (lang, userid, platform, text,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    if not stream_data('search', 'user_activity', log_data):
        print log_formatter(inspect.stack()[0][3], "failed logging request")

    try:
        pratilipi_count = 0
        author_count = 0

        #lang, read_count, name, gender, pen_name_en, follow_count,
        #profile_image, content_published, pen_name
        #reg_date, state, cover_image, name_en, summary, author_id

        state_filter = " AND state:ACTIVE" if is_active else ""
        lang_filter = " AND lang:%s" % lang if lang is not None else ""
        url = SOLR_URL
        url = "%s/solr/author/select" % url
        url = "%s?wt=json&q=*%s*%s%s" % (url, text, lang_filter, state_filter)
        url = "%s&fl=name,name_en,summary,score,read_count,author_id" % url
        url = "%s&sort=score desc,read_count desc" % url
        url = "%s&rows=%s&start=%s" % (url, limit, offset)
        #url = "%s&qf=name^200+name_en^200+summary^0.1" % url

        print log_formatter(inspect.stack()[0][3], "solr url %s" % url)

        author = []
        response = requests.get(url)
        if response.status_code == 200:
            data = json.loads(response.text)

            author_count = data['response']['numFound']
            for row in data['response']['docs']:
                temp = {}
                temp['author_id'] = row['author_id']
                temp['score'] = row['score']
                temp['read_count'] = row['read_count']
                if 'name' in row:
                    temp['name'] = row['name']
                if 'name_en' in row:
                    temp['name_en'] = row['name_en']
                if 'summary' in row:
                    temp['summary'] = row['summary']
                author.append(temp)

        #lang, read_count, pratilipi_type, review_count, total_rating, listing_date, title, title_en, state,
        # author_name, summary, genre, chapter_count, rating_count, content_type, cover_image, author_id, author_name_en
        state_filter = " AND state:PUBLISHED" if is_active else ""
        lang_filter = " AND lang:%s" % lang if lang is not None else ""
        url = SOLR_URL
        url = "%s/solr/pratilipi/select" % url
        url = "%s?wt=json&q=*%s*%s%s" % (url, text, lang_filter, state_filter)
        url = "%s&fl=title,title_en,summary,score,read_count,author_id" % url
        url = "%s,author_name,author_name_en,genre,pratilipi_id" % url
        url = "%s&sort=score desc,read_count desc" % url
        url = "%s&rows=%s&start=%s" % (url, limit, offset)

        print log_formatter(inspect.stack()[0][3], "solr url %s" % url)
        pratilipi = []
        pratilipi_count = 0
        response = requests.get(url)
        if response.status_code == 200:
            data = json.loads(response.text)

            pratilipi_count = data['response']['numFound']
            for row in data['response']['docs']:
                temp = {}
                temp['author_id'] = row['author_id']
                temp['pratilipi_id'] = row['pratilipi_id']
                temp['score'] = row['score']
                temp['read_count'] = row['read_count']
                if 'title' in row:
                    temp['title'] = row['title']
                if 'title_en' in row:
                    temp['title_en'] = row['title_en']
                if 'author_name' in row:
                    temp['author_name'] = row['author_name']
                if 'author_name_en' in row:
                    temp['author_name_en'] = row['author_name_en']
                if 'summary' in row:
                    temp['summary'] = row['summary']
                pratilipi.append(temp)

        response = {}
        if author_count > 0:
            response['authors_found'] = author_count
            response['authors'] = author
        if pratilipi_count > 0:
            response['pratilipis_found'] = pratilipi_count
            response['pratilips'] = pratilipi

        if not bool(response):
            return api_response(204, "No Content")

        print log_formatter(inspect.stack()[0][3], "search done")
        return api_response(200, "Success", response)
    except Exception as err:
        print "failed while searching - ", str(err)
        return api_response(500, 'Internal Server Error')


@route('/search')
def search():
    """
    search
    """
    print log_formatter(inspect.stack()[0][3], "search start")

    accepttxt = request.headers.get('Accept', "version=1.0")
    searchtxt = re.search(r'version=(\d.\d)', accepttxt.lower())
    version = 1.0
    if searchtxt:
        version = searchtxt.group()[-3:]

    userid = request.query.get('userid', None)
    text = request.query.get('text', None)
    lang = request.query.get('lang', None)
    platform = request.query.get('platform', 'web')
    is_active = request.query.get('is_active', True)
    limit = request.query.get('limit', 20)
    offset = request.query.get('offset', 0)

    if text is None:
        return api_response(400, "Bad Request")

    try:
        pratilipi_count = 0
        author_count = 0

        state_filter = "ACTIVE" if is_active else "*"
        lang_filter = '{}'.format(lang) if lang is not None else '*'
        param_dict = {'wt':'json', 
                      'fl':'author_id', 
                      'sort':'score desc, read_count desc', 
                      'rows':limit,
                      'start':offset,
                      'q':'*{}* AND state:{} AND lang:{}'.format(text, state_filter, lang_filter)}
        url = "{}/{}".format(SOLR_URL, "author/select")

        print log_formatter(inspect.stack()[0][3], "solr url %s" % url)

        author = []
        response = requests.get(url, params=param_dict)
        if response.status_code == 200:
            data = json.loads(response.text)
            author_count = data['response']['numFound']
            for row in data['response']['docs']:
                author.append(row['author_id'])

        state_filter = "PUBLISHED" if is_active else "*"
        lang_filter = '{}'.format(lang) if lang is not None else '*'
        param_dict = {'wt':'json', 
                      'fl':'pratilipi_id', 
                      'sort':'score desc, read_count desc', 
                      'rows':limit,
                      'start':offset,
                      'q':'*{}* AND state:{} AND lang:{}'.format(text, state_filter, lang_filter)}
        url = "{}/{}".format(SOLR_URL, "pratilipi/select")

        print log_formatter(inspect.stack()[0][3], "solr url %s" % url)
        pratilipi = []
        pratilipi_count = 0
        response = requests.get(url, params=param_dict)
        if response.status_code == 200:
            data = json.loads(response.text)
            pratilipi_count = data['response']['numFound']
            for row in data['response']['docs']:
                pratilipi.append(row['pratilipi_id'])

        response = {}
        if author_count > 0:
            response['authors_found'] = author_count
            url = "{}".format(AUTHOR_SERVICE)
            param_dict = {'id':author}
            service_response = requests.get(url, param=param_dict)
            if service_response.status_code == 200:
                response['authors'] = json.loads(service_response.text)
            else:
                print log_formatter(inspect.stack()[0][3], "call failed to author service")

        if pratilipi_count > 0:
            response['pratilipis_found'] = pratilipi_count
            url = "{}".format(PRATILIPI_SERVICE)
            param_dict = {'id':pratilipi}
            service_response = requests.get(url, param=param_dict)
            if service_response.status_code == 200:
                response['pratilips'] = json.loads(service_response.text)
            else:
                print log_formatter(inspect.stack()[0][3], "call failed to pratilipi service")

        if not bool(response):
            return api_response(204, "No Content")

        log_data = (lang, userid, platform, text,
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    response.get('authors_found', 0), response.get('pratilipis_found', 0))
        if not stream_data('search', 'user_activity', log_data):
            print log_formatter(inspect.stack()[0][3], "failed logging request")

        print log_formatter(inspect.stack()[0][3], "search done")
        return api_response(200, "Success", response)
    except Exception as err:
        print "failed while searching - ", str(err)
        return api_response(500, 'Internal Server Error')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("host", type=str, help="host")
    parser.add_argument("port", type=int, help="port")
    args = parser.parse_args()

    run(host=args.host, port=args.port)
