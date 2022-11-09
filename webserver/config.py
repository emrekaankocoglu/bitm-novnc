'''
Class Config for handling the config file. Currently only containing hosts available.

Also handles the load balancing behavior with round-robin decisions on hosts.

TODO: Replace round-robin decision making with geolocation-based host selection,
since 2FA also specifies where the request is sent from. Closer you are, better it is.

'''

import yaml
import itertools

class Config:
    def __init__(self,file_location):
        with open(file_location,'r') as file:
            self.config=yaml.safe_load(file)
        self.hosts=itertools.cycle(self.config["workers"]["hosts"])
    def getNextHost(self):
        return next(self.hosts)
