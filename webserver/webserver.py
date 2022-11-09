'''
Flask webserver for serving static files for noVNC and creating an endpoint for the creation of sessions.
TODO: Needs logging
'''
from flask import Flask, jsonify,request,abort
import requests
from config import Config

app=Flask(__name__,static_url_path='',static_folder='/noVNC-basic')

config=Config('config.yml')

# Gets a new session (and triggers the creation of one) from one of the workers
def getSession(target_url):
    global config
    # the next worker available-check config.py
    host=config.getNextHost()["host"]

    #worker endpoint for creating a session
    req_url="http://"+host["ip"]+":"+str(host["port"])+"/session/create"
    data={"url":target_url}

    # sends a request to worker
    # TODO: make it retry after the failed attempt to get a session here,
    # not in session().
    try:
        r=requests.post(req_url,json=data,timeout=3)
        print(r)
        response=r.json()
        response["host"]=host["ip"]
        return response
    except requests.exceptions.ConnectTimeout as e:
        print(e)
        return None

# Endpoint of the webserver for the client to send requests to, and get sessions.
# This is to avoid CORS restrictions.
# Of course, a better way to achieve this is 
# to serve the web page with the session credentials already baked in,
# but this does not make it into todo, because it is too big of a job:)

@app.route('/session', methods=['POST'])
def session():
    # get URL parameter sent from the client - see getSession() from noVNC-basic/vnc_lite.html
    params=request.get_json()
    if ("url" in params):
        url=params["url"]
    else:
        url=None

    # get the session
    s=getSession(target_url=url)

    # TODO: yes, thing to move is here, referenced on getSession()
    while s is None:
        s=getSession(target_url=url)

    return jsonify(s)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
    # TODO: Add a proper debug mode