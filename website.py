import os
import sys
import json
from flask import Flask, render_template


PAGES_FOLDER = r'./reports/' #sys.argv[1]
app = Flask(__name__, static_url_path='/static')

def reportsTab(html):
    reports = [x for x in os.listdir(PAGES_FOLDER) if ".html" in x][:10]
    return html.replace("``REPORTS``", '\n'.join(['<a href="{}">{}</a>'.format(PAGES_FOLDER + report[:report.find(".html")], report[:report.find(".html")]) for report in reports]))

@app.route('/')
def home():
    return reportsTab(open(r"./templates/home.html", 'r').read())

@app.route(PAGES_FOLDER[1:] + '<string:name>')
def reportPage(name):
    return  open(PAGES_FOLDER + name + ".html", 'r').read()

@app.route("/archived")
def archived():
    reports = [x for x in os.listdir(PAGES_FOLDER) if ".html" in x]
    page = ''
    for report in reports:
        page += '<li><a href="{}">{}</a></li>'.format(PAGES_FOLDER[1:] + report[: report.find(".html")], report[: report.find(".html")])
    return reportsTab(open(r"./templates/archived.html", 'r').read().replace("``PAGES``", page))

@app.route('/summarized')
def summarizedReportPage():
    # getting DB
    try:
        with open("DB.dat", "r") as file:
            db = json.loads(file.read())
    except:
        db = {}

    # getting summrized template
    with open(r"./templates/summarized.html", 'r') as file:
        copy = file.read()

    # editing
    try:
        copy = copy.replace(r"``REPORT_NAMES``", str([key for key in db.keys()]))
        
        POS = 0
        copy = copy.replace(r"``INCOMING_DATA``", str([sum(total[POS].values()) for total in db.values()]))
        copy = copy.replace(r"``INCOMING_AVG``", '[' +  (str(sum([sum(total[POS].values()) for total in db.values()])/len([sum(total[POS].values()) for total in db.values()])) + ', ')*(len([key for key in db.keys()]) - 1) + str(sum([sum(total[POS].values()) for total in db.values()])/len([sum(total[POS].values()) for total in db.values()])) + ']')

        POS = 1
        copy = copy.replace(r"``OUTGOING_DATA``", str([sum(total[POS].values()) for total in db.values()]))
        copy = copy.replace(r"``OUTGOING_AVG``", '[' +  (str(sum([sum(total[POS].values()) for total in db.values()])/len([sum(total[POS].values()) for total in db.values()])) + ', ')*(len([key for key in db.keys()]) - 1) + str(sum([sum(total[POS].values()) for total in db.values()])/len([sum(total[POS].values()) for total in db.values()])) + ']')

        copy = copy.replace(r"``ALERTS``", str([alerts[3] for alerts in db]))

        with open("./reports/tmp.html", 'w') as file:
            file.write(copy)

        return copy
    except:
        return copy.replace(r"``ALERTS``", "Not enough data to summarize").replace(r'''<div class="container">
        <h1>Incoming</h1>
        <canvas id="1" width="600" height="280"></canvas>
        <h1>Outgoing</h1>
        <canvas id="2" width="600" height="280"></canvas>
    </div>
''', "")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
