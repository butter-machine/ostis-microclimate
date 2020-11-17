import os.path
import json
from http.server import BaseHTTPRequestHandler

import matplotlib.pyplot as plt
import socketserver
from playsound import playsound

from sc import ScMemoryContext, ScAddr, ScType


PORT = 8088
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class OSTISService:
    def __init__(self):
        self.ctx = ScMemoryContext.Create('ChartServerContext')
        self.outrange_microclimate_record_addr = self.ctx.HelperResolveSystemIdtf(
            'outrange_microclimate_record',
            ScType.Unknown.NodeConstNoRole
        )

    def get_plot_data(self, data):
        return {
            'date': self.ctx.GetLinkContent(
                ScAddr(data['date_link_addr'])
            ).AsString(),
            'humidity': self.ctx.GetLinkContent(
                ScAddr(data['humi_link_addr'])
            ).AsFloat(),
            'temperature': self.ctx.GetLinkContent(
                ScAddr(data['temp_link_addr'])
            ).AsFloat()
        }

    def mark_outrange(self, record_addr):
        self.ctx.CreateEdge(ScType.EdgeAccessConstPosPerm, self.outrange_microclimate_record_addr, ScAddr(record_addr))


class Plotter:
    def __init__(self, ostis_service):
        self.ostis_service = ostis_service
        self.ax = plt.axes()
        self.x = list()
        self.y = list()
        self.max_y = 50
        self.min_y = 20
        self.play_sound = False
        plt.gcf().autofmt_xdate()

    def update(self, x, y, record_addr):
        with open('../../problem-solver/py/services/MicroClimateChartScript/config.json', 'r') as config_file:
            config_dict = json.loads(config_file.read())
        self.max_y = config_dict['max_temperature']
        self.min_y = config_dict['min_temperature']
        self.play_sound = config_dict['play_sound']

        if y > self.max_y or y < self.min_y:
            self.ostis_service.mark_outrange(record_addr)
            if self.play_sound:
                playsound('../../problem-solver/py/services/MicroClimateChartScript/warning.wav')

        plt.ylim(self.min_y - 5, self.max_y + 5)
        for line in self.ax.lines:
            line.remove()
        plt.axhline(self.max_y, 0, 1, color='red')
        plt.axhline(self.min_y, 0, 1, color='red')

        self.x.append(x)
        self.y.append(y)

        self.ax.scatter([x], [y])
        self.ax.plot(self.x, self.y, color='green')

        plt.draw()
        plt.pause(0.01)


class Handler(BaseHTTPRequestHandler):
    ostis_service = OSTISService()
    plotter = Plotter(ostis_service)

    def do_POST(self):
        self.send_response(200, 'ok')
        length = int(self.headers.get('content-length'))
        data = json.loads(self.rfile.read(length))

        plot_data = self.ostis_service.get_plot_data(data)
        x = plot_data['date'][13:-1]
        y = plot_data['temperature']
        if y == 'NaN':
            y = None
        else:
            y = float(y)
        record_addr = data['record_addr']
        self.plotter.update(x, y, record_addr)


class ChartServer:
    def __init__(self):
        self.stdin_path = '/dev/null'
        self.stdout_path = '/dev/tty'
        self.stderr_path = '/dev/tty'
        self.pidfile_path = '/tmp/foo.pid'
        self.pidfile_timeout = 5
        self.httpd = None

    def __del__(self):
        self.httpd.shutdown()
        plt.close('all')

    def run(self):
        with socketserver.TCPServer(('', PORT), Handler) as httpd:
            self.httpd = httpd
            print(f"Chart server: Serving at port {PORT}")
            httpd.serve_forever()


ChartServer().run()
