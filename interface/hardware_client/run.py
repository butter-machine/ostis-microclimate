from hardware_client import HardwareClient
from settings import URI

if __name__ == '__main__':
    try:
        HardwareClient(URI).run()
    except ConnectionRefusedError:
        print('Please, run OSTIS')
