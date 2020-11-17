import json
import asyncio
from http.client import RemoteDisconnected

import websockets
from datetime import datetime

from comport_connection import ComportConnection, ComportConnectionError
from serializers import ComportSerializer
from urllib.request import urlopen
import settings


IDTF = [
    'microclimate_record',
    'humidity',
    'temperature',
    'rrel_mesurement_time',
    'rrel_mesurement_place',
    'nrel_percental_mesurement',
    'nrel_celsius_mesurement',
    'office',
    'value',
    'number',
    'nrel_value'
]


class IDTFReceiver:
    def __init__(self, idtf):
        self._idtf = idtf
        self.idtf_ids = dict()

        self._init_idtf_ids()

    async def _receive_idtf(self, data):
        async with websockets.connect(settings.URI) as websocket:         
            await websocket.send(json.dumps(data))
            response = await websocket.recv()
            response = json.loads(response)

            self.idtf_ids = dict(zip(self._idtf, response['payload']))
            print('\nKyenodes received')

    def _init_idtf_ids(self):
        data = {
            'id': 1,
            'type': 'keynodes',
            'payload': []
        }

        for idtf in self._idtf:
            data['payload'].append({
                    'command': 'find',
                    'idtf': idtf
                })

        asyncio.get_event_loop().run_until_complete(self._receive_idtf(data))


class HardwareClient:
    def __init__(self, uri):
        self.request_id = 2
        self.mk_connection = ComportConnection()
        self.uri = uri
        self.serializer = ComportSerializer()
        self.idtf_receiver = IDTFReceiver(IDTF)

        try:
            self.mk_connection.connect()
        except ComportConnectionError:
            # The last attempt to reconnect. There are sometimes issues
            # with connection from the first time
            print('\nSomething went wrong. Retrying...')
            self.mk_connection.connect()
    
    def _get_data_to_send(self):
        mk_data = self.serializer.serialize()
        timestamp = str(datetime.now().strftime('%d-%b-%Y (%H:%M:%S)'))

        data = dict()
        data['id'] = self.request_id
        data['type'] = 'create_elements'

        payload = [
            # new instance of microclimate_record
            # 0
            {
                'el': 'node',
                'type': 1
            },
            # microclimate_record -> instance
            # 1
            {
                'el': 'edge',
                'src': {
                    'type': 'ref',
                    'value': 0
                },
                'trg': {
                    'type': 'addr',
                    'value': self.idtf_receiver.idtf_ids['microclimate_record']
                },
                'type': 2224
            },
            # instance -> office
            # 2
            {
                'el': 'edge',
                'src': {
                    'type': 'ref',
                    'value': 0
                },
                'trg': {
                    'type': 'addr',
                    'value': self.idtf_receiver.idtf_ids['office']
                },
                'type': 2224
            },
            # rrel_mesurement_place
            # 3
            {
                'el': 'edge',
                'src': {
                    'type': 'addr',
                    'value':  self.idtf_receiver.idtf_ids['rrel_mesurement_place']
                },
                'trg': {
                    'type': 'ref',
                    'value': 2
                },
                'type': 2224
            },
            # time mesurment instance
            # 4
            {
                'el': 'node',
                'type': 1
            },
            # instance -> time mesurment instance
            # 5
            {
                'el': 'edge',
                'src': {
                    'type': 'ref',
                    'value':  0
                },
                'trg': {
                    'type': 'ref',
                    'value': 4
                },
                'type': 2224
            },
            # rrel_mesurement_time
            # 6
            {
                'el': 'edge',
                'src': {
                    'type': 'addr',
                    'value':  self.idtf_receiver.idtf_ids['rrel_mesurement_time']
                },
                'trg': {
                    'type': 'ref',
                    'value': 5
                },
                'type': 2224
            },
            # link
            # 7
            {
                'el': 'link',
                'type': 1,
                'content': timestamp,
                'content_type': 'string'
            },
            # time mesurment instance => link
            # 8
            {
                'el': 'edge',
                'src': {
                    'type': 'ref',
                    'value':  4
                },
                'trg': {
                    'type': 'ref',
                    'value': 7
                },
                'type': 40
            },
            # humidity instance
            # 9
            {
                'el': 'node',
                'type': 1
            },
            # microclimate_record instance -> humidity instance
            # 10
            {

                'el': 'edge',
                'src': {
                    'type': 'ref',
                    'value':  0
                },
                'trg': {
                    'type': 'ref',
                    'value': 9
                },
                'type': 2224
            },
            # procental mesurement instance
            # 11
            {
                'el': 'node',
                'type': 1
            },
            # humidity instance => percental mesurement instance
            # 12
            {
                'el': 'edge',
                'src': {
                    'type': 'ref',
                    'value':  9
                },
                'trg': {
                    'type': 'ref',
                    'value': 11
                },
                'type': 40 
            },
            # nrel_percental_mesurement
            # 13
            {
                'el': 'edge',
                'src': {
                    'type': 'addr',
                    'value': self.idtf_receiver.idtf_ids['nrel_percental_mesurement']
                },
                'trg': {
                    'type': 'ref',
                    'value': 11
                },
                'type': 2224
            },
            # humidity value
            # 14
            {
                'el': 'link',
                'type': 1,
                'content': mk_data['humi'],
                'content_type': 'float'
            },
            # percental mesurement instance => humidity value
            # 15
            {
                'el': 'edge',
                'src': {
                    'type': 'ref',
                    'value': 11
                },
                'trg': {
                    'type': 'ref',
                    'value': 14
                },
                'type': 40 
            },
            # nrel_value
            # 16
            {
                'el': 'edge',
                'src': {
                    'type': 'addr',
                    'value': self.idtf_receiver.idtf_ids['nrel_value']
                },
                'trg': {
                    'type': 'ref',
                    'value': 15
                },
                'type': 2224
            },
            # temperature instance
            # 17
            {
                'el': 'node',
                'type': 1
            },
            # temperature -> temperature instance
            # 18
            {
                'el': 'edge',
                'src': {
                    'type': 'addr',
                    'value': self.idtf_receiver.idtf_ids['temperature']
                },
                'trg': {
                    'type': 'ref',
                    'value': 17
                },
                'type': 2224
            },
            # microclimate_record -> temperature instance
            # 19
            {
                'el': 'edge',
                'src': {
                    'type': 'ref',
                    'value': 1
                },
                'trg': {
                    'type': 'ref',
                    'value': 17
                },
                'type': 2224
            },
            # value -> temperature_instance
            # 20
            {

                'el': 'edge',
                'src': {
                    'type': 'addr',
                    'value': self.idtf_receiver.idtf_ids['value']
                },
                'trg': {
                    'type': 'ref',
                    'value': 17
                },
                'type': 2224
            },
            # value -> humidity_instance
            # 20
            {

                'el': 'edge',
                'src': {
                    'type': 'addr',
                    'value': self.idtf_receiver.idtf_ids['value']
                },
                'trg': {
                    'type': 'ref',
                    'value': 14
                },
                'type': 2224
            },
            # number instance
            # 21
            {
                'el': 'node',
                'type': 1
            },
            # temperature instance => number instance
            # 22
            {
                'el': 'edge',
                'src': {
                    'type': 'ref',
                    'value': 17
                },
                'trg': {
                    'type': 'ref',
                    'value': 21
                },
                'type': 40
            },
            # nrel_celsius_mesurement
            # 23
            {
                'el': 'edge',
                'src': {
                    'type': 'addr',
                    'value': self.idtf_receiver.idtf_ids['nrel_celsius_mesurement']
                },
                'trg': {
                    'type': 'ref',
                    'value': 22
                },
                'type': 2224
            },
            # number -> number_instance
            # 24
            {
                'el': 'edge',
                'src': {
                    'type': 'addr',
                    'value': self.idtf_receiver.idtf_ids['number']
                },
                'trg': {
                    'type': 'ref',
                    'value': 21
                },
                'type': 2224
            },
            # link
            # 25
            {
                'el': 'link',
                'type': 1,
                'content': mk_data['temp'],
                'content_type': 'float'
            },
            # number_instance => link
            # 26
            {
                'el': 'edge',
                'src': {
                    'type': 'ref',
                    'value': 21
                },
                'trg': {
                    'type': 'ref',
                    'value': 25
                },
                'type': 40
            },
            # nrel_value
            # 27
            {
                'el': 'edge',
                'src': {
                    'type': 'addr',
                    'value': self.idtf_receiver.idtf_ids['nrel_value']
                },
                'trg': {
                    'type': 'ref',
                    'value': 26
                },
                'type': 2224
            }
        ]

        data['payload'] = payload

        self.request_id += 1
        return data

    async def send_microclimate_parameters(self):
        async with websockets.connect(self.uri) as websocket:
            while True:
                data = self._get_data_to_send()              

                await websocket.send(json.dumps(data))

                response = await websocket.recv()
                response = json.loads(response)
                data = {
                    'record_addr': response['payload'][0],
                    'date_link_addr': response['payload'][7],
                    'humi_link_addr': response['payload'][14],
                    'temp_link_addr': response['payload'][26]
                }
                try:
                    urlopen("http://localhost:8088", json.dumps(data).encode())
                except RemoteDisconnected:
                    pass

                await asyncio.sleep(settings.REFRESH_SECONDS_INTERVAL)

    def run(self):
        asyncio.get_event_loop().run_until_complete(self.send_microclimate_parameters())
        asyncio.get_event_loop().run_forever() 
