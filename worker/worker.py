'''
Worker node with endpoints as a Flask app, 
run with wsgi server (or event handler) of your liking.
TODO: Needs logging
'''
from flask import Flask, jsonify,request,abort
import time
from session import Session
app=Flask(__name__,static_url_path='',static_folder='')

# Session list to keep created sessions
#TODO: Migrate this to a database for persistency
session_list=[]

def createSession(host="0.0.0.0",url=None):
    try:
        new_session=Session(host,url)
        new_session.activate()
        print(new_session)
        session_list.append(new_session)

    # TODO: Terrible exception handling, find a better way
    except Exception as e:
        print(e)
        return None

    return {"port":new_session.port_websocket}
    
@app.route('/session/create', methods=['POST'])
def session():
    # get desired URL from user request
    sessionRequest=request.json
    new_session=createSession(url=sessionRequest["url"])
    if new_session is None:
        return "Failed",503
    
    # This sleep is actually required, since noVNC hangs when either the VNC server
    # or the WebSocket proxy is not running
    # TODO: Either introduce a signaling mechanism or make noVNC retry on failure
    time.sleep(1)

    return jsonify(new_session)

if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=8080)

    # Kill subprocesses on a KeyboardInterrupt when running in debug mode
    # TODO: Add a proper debug mode
    except:
        for x in session_list:
            try:
                x.deactivate()
            except:
                print("Error at deletion")
