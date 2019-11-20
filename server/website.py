import os
import sys
import logging
from flask import Flask

PAGE_OUT = sys.argv[1]
app = Flask(__name__)

@app.route('/')
def home():
    reports = [x for x in os.listdir(PAGE_OUT) if ".html" in x]
    page = "<h2>this</h2>\n"
    for report in reports:
        page += '<a href="{}">{}</a>\n'.format(PAGE_OUT + report, report[: report.find(".html")])
    return page

@app.route('/pages/<string:name>')
def reportPage(name):
    with open(PAGE_OUT + name, 'r') as file:
        return file.read()
    return "An error has occurred"

if __name__ == "__main__":
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    app.run(host="127.0.0.1", port=80)
