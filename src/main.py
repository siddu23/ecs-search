"""Search Microservice v1.0
Primary gateway to get data from pratilipi data store
currently supports search of -
- authors
- pratilipis (content)
"""

import os
import sys

# set the base path
sys.path.append("%s/lib" % os.getcwd())
base_path = os.path.abspath(os.path.dirname(__file__))

import argparse
import ConfigParser
import requests
import inspect
import simplejson as json
import re

from datetime import datetime
from bottle import route, run, request, response, template
import bigquery_ops


# fetch config
config_path = "%s/%s" % (base_path.replace('src', 'config'), "search.cnf")
search_config = ConfigParser.RawConfigParser()
search_config.read(config_path)
url_path = search_config.get("SOLR", "BASE_URL")


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


@route('/ping')
def ping():
    """
    ping - to check if the api is up
    """
    return log_formatter(inspect.stack()[0][3], "pong")


@route('/create_core')
def create_core():
    """
    create a new core
    """
    name = request.query['name']
    url = "%s/solr/admin/cores?action=CREATE&name=%s" % (url_path, name)
    req = requests.get(url)
    if req.status_code == 200:
        return api_response(req.status_code, req.text)
    return api_response(req.status_code, req.text)


@route('/add_row', method='POST')
def add_row():
    """
    add an entry to solr core
    """
    name = request.forms['name']
    data = request.forms['data']

    row = { "add": {
        "doc": "data",
        "commitWithin": 5,
        "overwrite": "false" } }
    
    url = "%s/solr/%s/update?commit=true" % (url_path, name)
    print "=====> ", url
    req = requests.post(
        url, data, {":content_type": "application/json", ":accept": "application/json"})
    return api_response(req.status_code, req.text)



@route('/delete')
def update(core_name, data):
    """
    update an entry to solr core
    """
    name = request.forms['name']
    data = request.forms['data']

    url = url_path + "/solr/%s/update?commit=true" % core_name
    req = requests.post(
        url, data, {":content_type": "application/json", ":accept": "application/json"})
    return api_response(req.status_code, req.text)


@route('/update')
def delete(core_name, data):
    """
    delete an entry from solr core
    """
    url = url_path + "/solr/%s/update?commit=true" % core_name
    req = requests.post(
        url, data, {":content_type": "application/json", ":accept": "application/json"})
    return api_response(req.status_code, req.text)


@route('/file_uploader')
def file_uploader():
    """
    upload file in batches to solr core
    """
    name = request.query['name']
    filename = request.query['filename']

    response = fileuploader()
    return api_response(response['status_code'], response['text'], response['data'])



@route('/search')
def search():
    """
    search
    """
    print log_formatter(inspect.stack()[0][3], "search start")

    accepttxt = request.headers.get('Accept', "version=1.0")
    searchtxt = re.search( r'version=(\d.\d)', accepttxt.lower())
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
        
    log_data = (lang, userid, platform, text, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    if not bigquery_ops.stream_data('search', 'user_activity', log_data):
        print log_formatter(inspect.stack()[0][3], "failed logging request")

    try:
        pratilipi_count = 0
        author_count = 0

        #lang, read_count, name, gender, pen_name_en, follow_count, 
        #profile_image, content_published, pen_name
        #reg_date, state, cover_image, name_en, summary, author_id

        state_filter = " AND state:ACTIVE" if is_active else ""
        lang_filter = " AND lang:%s" % lang if lang is not None else ""
        url = url_path 
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
        url = url_path
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


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("host", type=str, help="host")
    parser.add_argument("port", type=int, help="port")
    args = parser.parse_args()

    run(host=args.host, port=args.port)

