"""
Pratilipi Search Data Uploader
Currently support search indexes are
- Author
- Pratilipi
"""

import os
import io
import sys
import gzip
import simplejson as json
import csv

PATH = '/home/gauri/Downloads/solr_data'


"""
old_os_path = os.environ.get('PATH', '')
os.environ['PATH'] = os.path.dirname(os.path.abspath(__file__)) + os.pathsep + old_os_path
base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if sys.platform == 'win32':
    site_packages = os.path.join(base, 'Lib', 'site-packages')
else:
    site_packages = os.path.join(base, 'lib', 'python%s' % sys.version[:3], 'site-packages')
prev_sys_path = list(sys.path)
"""


def readfile(filepath):
    """
    lazy read file line by line
    """
    with open(filepath, 'r') as file_obj:
        for line in file_obj:
            yield line.strip()


# Authors Data
input_file_name = PATH + '/AUTHOR'
#input_file_name = PATH + '/test.json'
out_file_name = PATH + '/author_solr.json.gz'
author = {}
line_cntr = 0
failed_line_cntr = 0

try:
    with gzip.open(out_file_name, 'wb') as out_file_obj:
        for line in readfile(input_file_name):
            row = json.loads(line.strip())

            try:
                temp = {}
                temp['author_id'] = row['AUTHOR_ID']
                author[row['AUTHOR_ID']] = {}
                temp['user_id'] = 0
                if 'USER_ID' in row:
                    temp['user_id'] = row['USER_ID']
                    author[row['AUTHOR_ID']]['user_id'] = temp['user_id']
                if 'FIRST_NAME' in row and row['FIRST_NAME'] is not None:
                    temp['name'] = row['FIRST_NAME']
                if 'LAST_NAME' in row and row['LAST_NAME'] is not None:
                    if 'name' in temp:
                        temp['name'] = "%s %s" % (temp['name'], row['LAST_NAME'])
                    else:
                        temp['name'] = row['LAST_NAME']
                if 'name' in temp:
                    author[row['AUTHOR_ID']]['name'] = temp['name']
                if 'FIRST_NAME_EN' in row and row['FIRST_NAME_EN'] is not None:
                    temp['name_en'] = row['FIRST_NAME_EN']
                if 'LAST_NAME_EN' in row and row['LAST_NAME_EN'] is not None:
                    if 'name_en' in temp:
                        temp['name_en'] = "%s %s" % (temp['name_en'], row['LAST_NAME_EN'])
                    else:
                        temp['name_en'] = row['LAST_NAME_EN']
                if 'name_en' in temp:
                    author[row['AUTHOR_ID']]['name_en'] = temp['name_en']
                temp['content_published'] = row.get('CONTENT_PUBLISHED', 0)
                temp['follow_count'] = row.get('FOLLOW_COUNT', 0)
                if 'LANGUAGE' in row and row['LANGUAGE'] is not None:
                    temp['lang'] = row['LANGUAGE']
                temp['state'] = row['STATE']
                if 'GENDER' in row and row['GENDER'] is not None:
                    temp['gender'] = row['GENDER']
                if 'PEN_NAME' in row and row['PEN_NAME'] is not None:
                    temp['pen_name'] = row['PEN_NAME']
                if 'PEN_NAME_EN' in row and row['PEN_NAME_EN'] is not None:
                    temp['pen_name_en'] = row['PEN_NAME_EN']
                if 'SUMMARY' in row and row['SUMMARY'] is not None:
                    temp['summary'] = row['SUMMARY']
                temp['read_count'] = row.get('TOTAL_READ_COUNT', 0)
                temp['reg_date'] = row['REGISTRATION_DATE']
                if 'PROFILE_IMAGE' in row and row['PROFILE_IMAGE'] is not None:
                    temp['profile_image'] = row['PROFILE_IMAGE']
                if 'COVER_IMAGE' in row and row['COVER_IMAGE'] is not None:
                    temp['cover_image'] = row['COVER_IMAGE']
            except Exception as err:
                print "Failed while procesing Author line - ", str(err), line
                failed_line_cntr = line_cntr + 1
                continue

            try:
                outLine = json.dumps(temp)
                out_file_obj.write(outLine)
                out_file_obj.write('\n')
            except Exception as err:
                print "Failed while writing to Author output file - ", str(err), line
                failed_line_cntr = line_cntr + 1
                continue

            line_cntr = line_cntr + 1
except Exception as err:
    print "Failed while reading Author data - ", str(err)


print "Author Total: ", line_cntr, " Failed: ", failed_line_cntr

#sys.exit(1)


# Category Data
#tag data
input_file_name = PATH + '/TAG.csv'
tag = {}
try:
    with open(input_file_name, 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for row in reader:
            tag[row[0]] = ','.join([row[2], row[3], row[4]])
except Exception as err:
    print "Failed while reading Tag data - ", str(err)


#pratilipi tag data
input_file_name = PATH + '/PRATILIPI_TAG.csv'
pratilipi_tag_map = {}
try:
    with open(input_file_name, 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for row in reader:
            genre = None
            if row[1] in tag:
                genre = tag[row[1]]

            if genre is None:
                continue

            if row[0] not in pratilipi_tag_map:
                pratilipi_tag_map[row[0]] = genre
            else:
                pratilipi_tag_map[row[0]] = ','.join([pratilipi_tag_map[row[0]], genre])
except Exception as err:
    print "Failed while reading Pratilipi Tag data - ", str(err)

tag = {}


# Pratilipi Data
input_file_name = PATH + '/PRATILIPI'
#input_file_name = PATH + '/pratilipi.json'
out_file_name = PATH + '/pratilipi_solr.json.gz'
line_cntr = 0
failed_line_cntr = 0

try:
    with gzip.open(out_file_name, 'wb') as out_file_obj:
        for line in readfile(input_file_name):
            row = json.loads(line.strip())

            try:
                temp = {}
                temp['pratilipi_id'] = row['PRATILIPI_ID']
                temp['author_id'] = row['AUTHOR_ID']
                temp['chapter_count'] = row.get('CHAPTER_COUNT', 0)
                if 'COVER_IMAGE' in row and row['COVER_IMAGE'] is not None:
                    temp['cover_image'] = row['COVER_IMAGE']
                if 'LANGUAGE' in row and row['LANGUAGE'] is not None:
                    temp['lang'] = row['LANGUAGE']
                temp['state'] = row['STATE']
                temp['listing_date'] = row['LISTING_DATE']
                temp['content_type'] = row['CONTENT_TYPE']
                temp['pratilipi_type'] = row['PRATILIPI_TYPE']
                temp['rating_count'] = row.get('RATING_COUNT', 0)
                temp['review_count'] = row.get('REVIEW_COUNT', 0)
                temp['read_count'] = row.get('READ_COUNT', 0)
                if 'SUMMARY' in row and row['SUMMARY'] is not None:
                    temp['summary'] = row['SUMMARY']
                if 'TITLE' in row and row['TITLE'] is not None:
                    temp['title'] = row['TITLE']
                if 'TITLE_EN' in row and row['TITLE_EN'] is not None:
                    temp['title_en'] = row['TITLE_EN']
                temp['total_rating'] = row.get('TOTAL_RATING', 0)
                temp['genre'] = pratilipi_tag_map.get(temp['pratilipi_id'], None)
                if row['AUTHOR_ID'] in author:
                    if 'name' in author[row['AUTHOR_ID']]:
                        temp['author_name'] = author[row['AUTHOR_ID']]['name']
                    if 'name_en' in author[row['AUTHOR_ID']]:
                        temp['author_name_en'] = author[row['AUTHOR_ID']]['name_en']
                    temp['user_id'] = author[row['AUTHOR_ID']]['user_id']
            except Exception as err:
                print "Failed while procesing Pratilipi line - ", str(err), line
                failed_line_cntr = failed_line_cntr + 1
                continue

            try:
                outLine = json.dumps(temp)
                out_file_obj.write(outLine)
                out_file_obj.write('\n')
            except Exception as err:
                print "Failed while writing to Pratilipi output file - ", str(err), line
                failed_line_cntr = failed_line_cntr + 1
                continue

            line_cntr = line_cntr + 1
except Exception as err:
    print "Failed while reading Pratilipi data - ", str(err)


print "Pratilipi Total: ", line_cntr, " Failed: ", failed_line_cntr


