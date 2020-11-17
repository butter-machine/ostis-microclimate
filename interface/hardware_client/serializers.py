import os
import serial
import json

import settings

class ComportSerializer:
    def __init__(self):
        config_data = None
        with open(settings.CONFIGFILE) as json_file:
            config_data = json.load(json_file)

        self.comport = serial.Serial(
            config_data['comport'],
            config_data['baudrate'],
            timeout=config_data['timeout']
        )
    
    def serialize(self):
        data = self.comport.readline().decode('utf8')[:-2]
        if data != '__transmitting':
            data = json.loads(data)
        
        return data
