"""unit test cases for search
currently handles
- single keyword
- multiple keywords
- multi lingular keyword
- html entities

TODO
- fuziness
- filters
"""

import os
import sys
import argparse

# set the base path
sys.path.append("%s/lib" % os.getcwd())
BASE_PATH = os.path.abspath(os.path.dirname(__file__))

import simplejson as json
import requests
from openpyxl import load_workbook
from datetime import datetime

parser = argparse.ArgumentParser()
parser.add_argument("debug", type=bool, help="debug mode")
args = parser.parse_args()

url = 'http://localhost:2579/search'
wb = load_workbook(filename='{}/{}'.format(BASE_PATH, 'testcases.xlsx'), read_only=True)
ws = wb['Sheet1']

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

total = 0
failed = 0

for row in ws.rows:
    for cell in row:
        total = total + 1
        param_dict = {'text':cell.value}
        service_response = requests.get(url, params=param_dict)
        if service_response.status_code == 200:
            if json.loads(service_response.text)["response_header"]["status_code"] == 200:
                if not args.debug:
                    print "{} [OK] {} - {}\n{}".format(bcolors.OKGREEN, bcolors.ENDC, cell.value, json.loads(service_response.text)["response"])
                else:
                    print "{} [OK] {}".format(bcolors.OKGREEN, bcolors.ENDC)
                    print cell.value
            else:
                print "{} [Fail] {} - {}".format(bcolors.FAIL, bcolors.ENDC, cell.value)
                failed = failed  + 1
        else:
            print "{} [Fail] {} - {}".format(bcolors.FAIL, bcolors.ENDC, cell.value)
            failed = failed  + 1


print "Total - {} ; Failed - {}".format(total, failed)
