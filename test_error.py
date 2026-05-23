import urllib.request, urllib.error; 

try:
    urllib.request.urlopen('http://127.0.0.1:8000/raporlar/ticket/pdf/')
except urllib.error.HTTPError as e:
    text = e.read().decode()
    for line in text.split('\n'):
        if 'URI DID NOT MATCH' in line:
            print(line.strip())
