import os


URI = "ws://localhost:8090/ws_json"

DIRPATH =  os.path.dirname(os.path.realpath(__file__))
CONFIGFILE = os.path.join(DIRPATH, 'configs.json')
CONFIG_FIELDNAMES = ['port', 'baudrate', 'timeout']

REFRESH_SECONDS_INTERVAL = 3
