import os
import sys
import json
import logging
from flask import Flask, render_template


PAGES_FOLDER = r'./reports/' #sys.argv[1]
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
                <ul id="Reports" style="list-style-type: disc;">
                    <li><a href="summarized">Summarized</a></li>
                '''
    for report in reports:
        page += '<li><a href="{}">{}</a></li>'.format(PAGES_FOLDER + report, report[: report.find(".html")])
    return page + "</ul></body>"

@app.route(PAGES_FOLDER[1:] + '<string:name>')
def reportPage(name):
    return  open(r"./reports/" + name, 'r').read()


@app.route('/summarized')
def summarizedReportPage():
    # getting DB
    with open("DB.dat", "r") as file:
        db = json.loads(file.read())

    # getting summrized template
    with open(r"./templates/summarized.html", 'r') as file:
        copy = file.read()

    # editing
    try:
        copy = copy.replace(r"``REPORT_NAMES``", str([key for key in db.keys()]))
        
        POS = 0
        copy = copy.replace(r"``INCOMING_DATA``", str([sum(total[POS].values()) for total in [report for report in db.values()]]))
        copy = copy.replace(r"``INCOMING_AVG``", '[' +  (str(sum([sum(total[POS].values()) for total in [report for report in db.values()]])/len([sum(total[POS].values()) for total in [report for report in db.values()]])) + ', ')*(len([key for key in db.keys()]) - 1) + str(sum([sum(total[POS].values()) for total in [report for report in db.values()]])/len([sum(total[POS].values()) for total in [report for report in db.values()]])) + ']')

        POS = 1
        copy = copy.replace(r"``OUTGOING_DATA``", str([sum(total[POS].values()) for total in [report for report in db.values()]]))
        copy = copy.replace(r"``OUTGOING_AVG``", '[' +  (str(sum([sum(total[POS].values()) for total in [report for report in db.values()]])/len([sum(total[POS].values()) for total in [report for report in db.values()]])) + ', ')*(len([key for key in db.keys()]) - 1) + str(sum([sum(total[POS].values()) for total in [report for report in db.values()]])/len([sum(total[POS].values()) for total in [report for report in db.values()]])) + ']')

        copy = copy.replace(r"``ALERTS``", "Something here")

        with open("./reports/tmp.html", 'w') as file:
            file.write(copy)

        return copy
    except ZeroDivisionError:
        return "No data to summarize"

if __name__ == "__main__":
    # log = logging.getLogger('werkzeug')
    # log.setLevel(logging.ERROR)
    app.run(host="0.0.0.0", port=80)
