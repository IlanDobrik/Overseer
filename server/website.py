import os
import sys
import logging
from flask import Flask

@app.route('/')
def home(request):
    print(request)
    reports = [x for x in os.listdir(PAGE_OUT) if ".html" in x]
    page = "<h2>this</h2>\n"
    for report in reports:
        page += '<a href="{}">{}</a>\n'.format(PAGE_OUT + report, report[: report.find(".html")])
    return page
    
@app.route('/pages/<string:name>')
def reportPage(request, name):
    print(request, name)
    with open(PAGE_OUT + name, 'r') as file:
        return file.read()
    return "An error has occurred"

PAGE_OUT = sys.argv[1]
app = Flask(__name__)
log = logging.getLogger('werkzeug')
log.disabled = True