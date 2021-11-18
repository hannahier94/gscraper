import json

def fetch_json(inputfile, folder=None):
    """ Opens and loads JSONs """
    if not folder:
        folder = ""
    filepath = folder + inputfile
    with open(filepath) as f:
        data = json.load(f)

    return data

def write_json_file(data, filename="results.json"):
    """ Writes/creates a JSON file """
    with open(filename, 'w+') as outfile:
        json.dump(data, outfile)

