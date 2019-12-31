import os
import sys
import logging
from flask import Flask, render_template


PAGES_FOLDER = r'./templates/' #sys.argv[1]
app = Flask(__name__)

@app.route('/')
def home():
    reports = [x for x in os.listdir(PAGES_FOLDER) if ".html" in x]
    page = '''
                <title>Reports</title>
                <style>
                    body {
                        font-family: "Arial Black";
                        font-size: 20px;
                        }
                </style>
                <body>
                <h1>Reports</h1>
                <ul id="Reports" style="list-style-type: disc;">'''
    for report in reports:
        page += '<li><a href="{}">{}</a></li>'.format(PAGES_FOLDER + report, report[: report.find(".html")])
    return page + "</ul></body>"

@app.route(PAGES_FOLDER[1:] + '<string:name>')
def reportPage(name):
    print(name)
    return  render_template(name)

if __name__ == "__main__":
    # log = logging.getLogger('werkzeug')
    # log.setLevel(logging.ERROR)
    app.run(host="0.0.0.0", port=80)
