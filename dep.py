
import requests
from flask import Flask, render_template, request, redirect, url_for
from flask_wtf import CSRFProtect

import json
from datetime import datetime
import os



def fetch_json(inputfile, folder=None):
    """ Opens and loads JSONs """
    if not folder:
        folder = ""
    filepath = folder + inputfile
    with open(filepath) as f:
        data = json.load(f)

    return data

app = Flask(__name__)
SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY
google_custom_search_engine_id = "12613bf57ff548036"
google_custom_search_api_key = "AIzaSyCGwodHXdMM-Q2cNe_cw66W-w9Go4DgB9g"
csrf = CSRFProtect(app)
possible_classes = ['-','Good', 'Not Good', '-']

results = fetch_json("test.json")[:3]




@app.route('/classify', methods=('GET', 'POST'))
def classify():
    params = fetch_json("results.json")
    request_method = request.method
    buttons_list = fetch_json("util_vars.json")["buttons_vals"]
    # If classification is submitted
    if request_method == 'POST':
        classifications = {k: v for k, v in request.form.items()}
        return render_template('submission.html')



    return render_template('basicdisplay.html',
                           results=params,
                           buttons_list=buttons_list)

def write_json_file(data, filename="results.json"):
    with open(filename, 'w+') as outfile:
        json.dump(data, outfile)


@app.route("/", methods=['GET', 'POST'])
def home():
    # Get search request param
    search_string = request.args.get('searchString', '')
    search_start = request.args.get('searchStart', '1')
    page_size = 10

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
    results = data.get('items')[:5]
    num_results = len(results) #int(data.get('searchInformation').get('totalResults'))
    search_result_message = 'No results found ({} seconds)'.format(
        search_time) if num_results == 0 else 'About {} results ({} seconds)'.format(
        num_results, search_time)

    request_method = request.method
    # If client inputs search
    if search_string != '' and num_results > 0:
        write_json_file(results)
        print('Posting....')
        # Make a dictionary of the parameters from the form dictionary
        # params = {k: v for k, v in request.form.items()}
        # print('\n\n', params)
        # Send parameters to the new route to create the simulation
        return redirect(url_for("classify"))

    # Before client inputs parameters, use this template with blank parameters for them
    return render_template('home.html', search_string=search_string,
                           search_result_message=search_result_message,
                           num_results=num_results, search_start=search_start,
                           search_time=search_time, results=results,
                           page_size=page_size, possible_classes= possible_classes)




if __name__ == '__main__':

    port = os.environ.get('PORT')
    if port:
        app.run(host='0.0.0.0', port=int(port))
    else:
        app.run()
