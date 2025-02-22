import webbrowser 
import json
import subprocess
from googlesearch import search

try:
    with open('Data/websites.json', "r" ) as file:
        websites = json.load(file)
    
except Exception as e:
    print(f"[Error] Loading website Failed: {e}")
    websites = {}
    
def google_search_web(name):
    try:
        for url in search(name, num_results=1):
            return url
    except Exception as e:
        print(f"[Error] An error occur : {e}")
    return None

def add_in_json(name, url):
    websites[name] = url
    try:
        with open('Data/websites.json', "w") as file:
            json.dump(websites, file, indent=4)
    except Exception as e:
        print(f"Error {e}")
        
def open_web(name):
    web_name = name.lower().split()
    counts ={}
    for name in web_name:
        counts[name] = counts.get(name, 0) + 1
        
    url_to_open = []
    for name , count in counts.items():
        if name in websites:
            url_to_open.extend([websites[name]]* count)
        
        else:
            url = google_search_web(name=name)
            
            if url:
                print(f"{url} Found")
                add_in_json(name, url)
                url_to_open.extend([url]* count) 
            else:
                print(f"No website found for '{name}'")
    for url in url_to_open:
        webbrowser.open(url)
        
    if url_to_open:
        print(f"Opening {url_to_open} web.")
        
    else:
        print("No web found")   


          