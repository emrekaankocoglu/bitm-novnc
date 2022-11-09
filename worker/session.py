'''
Class Session for creating browser sessions users connect to.
'''

import subprocess
import os
import signal
import socket
import random
import time
import threading


class Session:
    def availablePort(self):
        # check for available ports for VNC and websocket
        result=False
        while result==False:
            port=random.randint(6000,6800)
            sock=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result=sock.connect_ex(('0.0.0.0', port))
        return str(port)

    def deactivate(self):
        if self.active:
            # send SIGTERM to avoid zombie processes
            os.kill(self.proc.pid, signal.SIGTERM)
            self.active = False

    def activate(self):
        # assigning ports
        self.port_vnc=self.availablePort()
        self.port_websocket=self.availablePort()
        while self.port_vnc==self.port_websocket:
            self.port_websocket=self.availablePort()

        # creation time and ports are used as a key for the session
        self.creation_time=str(int(time.time()))
        self.proc=subprocess.Popen(["bash","./start_tiger.sh",self.initial_resolution[0]+"x"+self.initial_resolution[1],
                                self.port_vnc,self.port_websocket,self.url,self.creation_time])
        if self.proc.returncode!=None:
            raise OSError("Process exited, either of the processes returned an error")

        self.active=True

        # process id is stored to be able to terminate the process afterwards
        # subprocess cannot handle child processes with this configuration, so subprocess.kill is useless
        self.pid = self.proc.pid

        # destroy the session 5 minutes after its creation
        destroy_timer=threading.Timer(300.0,self.deactivate,[])
        destroy_timer.start()

    def __init__(self,host,url=None,initial_resolution=None,port_vnc=None,
                port_websocket=None,active=False):
        
        # most of these attributes are for future-proofing and debugging purposes
        # TODO: relics of old design decisions, needs cleanup
    
        self.host = host
        self.creation_time=None
        self.url = url if url is not None else "https://accounts.google.com"
        self.initial_resolution = initial_resolution if initial_resolution is not None else ["1920","1080"]
        self.port_vnc=port_vnc
        self.port_websocket=port_websocket
        self.pid = None
        self.active = self.activate() if active is None else active

    def __str__(self):
        return '''Session host: {}, 
ports: {}(vnc) {}(ws), active: {},
creation time: {},
url: {}, initial resolution:  {}, pid: {}.'''.format(self.host,self.port_vnc,self.port_websocket,self.active,self.creation_time,self.url,self.initial_resolution,self.pid)

