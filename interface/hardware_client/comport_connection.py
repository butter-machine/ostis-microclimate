import sys
import glob
import serial
import json

import tqdm

import settings


class ComportConnectionError(Exception):
    pass


class ComportConnection:
    def __init__(self):
        self.baudrate = 0
        self.timeout = 0
        self.port = None
        self.configs = self._get_configs()

    def _get_configs(self):
        configs = dict()
        with open(settings.CONFIGFILE) as json_file:
            config_data = json.load(json_file)
            for field_name in settings.CONFIG_FIELDNAMES:
                try:
                    configs.update({field_name: config_data[field_name]})
                except KeyError:
                    configs.update({field_name: None})
        
        return configs

    def connect(self):
        self.configs = self._get_configs()
        self.baudrate = self.configs['baudrate']
        self.timeout = self.configs['timeout']

        if sys.platform.startswith('win'):
            ports = ['COM{}'.format(i + 1) for i in range(256)]
        elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
            # this excludes current terminal "/dev/tty"
            ports = glob.glob('/dev/tty[A-Za-z]*')
        else:
            raise EnvironmentError('Unsupported platform')

        print('\nCalling ports...')
        for port_ in tqdm.tqdm(ports):
            try:
                micro_controller = serial.Serial(port_, self.baudrate, timeout=self.timeout)
            except (OSError, serial.SerialException):
                pass
            else:
                if micro_controller.readline() == b'__transmitting\r\n':
                    micro_controller.flushInput()
                    micro_controller.write(b'__received')

                    config_data = {
                        'baudrate': self.baudrate,
                        'timeout': self.timeout,
                        'comport': port_,
                    }

                    with open(settings.CONFIGFILE, 'w') as outfile:
                        json.dump(config_data, outfile, indent=4)
                    
                    self.port = port_
                    micro_controller.close()

        if self.port:
            print('Working with {}, {} baudrate'.format(self.port, self.baudrate))
        else:
            raise ComportConnectionError
