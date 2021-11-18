
import requests
from flask import Flask, render_template, request, redirect, url_for
from flask_wtf import CSRFProtect

import json
from datetime import datetime
import os
import psycopg2

DATABASE_URL = os.environ['DATABASE_URL']

conn = psycopg2.connect(DATABASE_URL, sslmode='require')

app = Flask(__name__)
SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY
google_custom_search_engine_id = "12613bf57ff548036"
google_custom_search_api_key = "AIzaSyCGwodHXdMM-Q2cNe_cw66W-w9Go4DgB9g"
csrf = CSRFProtect(app)


@app.route('/classify', methods=('GET', 'POST'))
def classify():
    db = DbBuild()
    search_string = session.get('search_string', None)
    params = fetch_json("results.json")
    request_method = request.method
    buttons_list = fetch_json("utils_vars.json")["buttons_vals"]
    # If classification is submitted
    if request_method == 'POST':
        classifications = {k: v for k, v in request.form.items()}
        _ = db.write_lines(classifications, search_string)
        return render_template('submission.html')



    return render_template('basicdisplay.html',
                           results=params,
                           buttons_list=buttons_list)


def filter_results(results):
    db = DbBuild()
    return db.check_urls(results, limit=results_display_lim)

def fetch_start_string(search_string):
    db = DbBuild()
    return db.check_previous_searches(search_string)

@app.route("/", methods=['GET', 'POST'])
def home():
    # Get search request param
    search_string = request.args.get('searchString', '')
    session['search_string'] = search_string
    search_start = fetch_start_string(search_string)#request.args.get('searchStart', '1')
    page_size = 70

    if search_string == '':
        return render_template('home.html', search_string='',
                               search_result_message='', num_results=0,
                               page_size=page_size)

    # Construct URL and call API, receive results
    url = 'https://www.googleapis.com/customsearch/v1?q={}&start={}&cx={}&key={}'.format(
        search_string, search_start, google_custom_search_engine_id,
        google_custom_search_api_key)
    response = requests.get(url)

    if response.status_code != 200:
        search_result_message = 'Search returned an error: {} {}'.format(
            response.status_code, response.reason)
        return render_template('home.html', search_string=search_string,
                               search_result_message=search_result_message,
                               num_results=0, page_size=page_size)

    # Render search results
    data = response.json()

    search_time = datetime.now() #data.get('searchInformation').get('formattedSearchTime')
    initial_results = data.get('items')[:results_search_lim]
    results = filter_results(initial_results)
    num_results = len(results)
    search_result_message = 'No results found ({} seconds)'.format(
        search_time) if num_results == 0 else 'About {} results ({} seconds)'.format(
        num_results, search_time)

    request_method = request.method
    # If client inputs search
    if search_string != '' and num_results > 0:
        write_json_file(results)
        print('Posting....')
        return redirect(url_for("classify"))

    # Before client inputs parameters, use this template with blank parameters for them
    return render_template('home.html', search_string=search_string,
                           search_result_message=search_result_message,
                           num_results=num_results, search_start=search_start,
                           search_time=search_time, results=results,
                           page_size=page_size)

if __name__ == '__main__':

    port = os.environ.get('PORT')
    if port:
        app.run(host='0.0.0.0', port=int(port))
    else:
        app.run()
