from klein import run, route

@route('/')
def home(request):
    print(request)
    reports = [x for x in os.listdir(PAGE_OUT) if ".html" in x]
    page = ""
    for report in reports:
        page += '<a href="{}">{}\n</a>'.format(PAGE_OUT + report, report[: report.find(".html")])
    return page
    
@route('/pages/<string:name>')
def reportPage(request, name):
    print(request, name)
    with open(PAGE_OUT + name, 'r') as file:
        return file.read()
    return "An error has occurred"


run("localhost", 80)