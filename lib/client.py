import requests
import stem
import time
import random
from fake_useragent import UserAgent
from stem.control import Controller


class Client:

    def __init__(self, session=None):
        self.proxies = None
        self.headers = {'UserAgent': UserAgent().random}

    def request(self, *args, method='GET', **kwargs):
        if method == 'GET':
            return self.get(*args, **kwargs)
        elif method == 'POST':
            return self.post(*args, **kwargs)
        elif method == 'PUT':
            return self.put(*args, **kwargs)
        elif method == 'PATCH':
            return self.patch(*args, **kwargs)
        elif method == 'DELETE':
            return self.delete(*args, **kwargs)
        else:
            raise Exception('Invalid HTTP method specified!')

    def get(self, *args, **kwargs):
        return requests.get(*args, proxies=self.proxies, headers=self.headers, **kwargs)

    def post(self, *args, **kwargs):
        return requests.get(*args, proxies=self.proxies, headers=self.headers, **kwargs)

    def put(self, *args, **kwargs):
        return requests.put(*args, proxies=self.proxies, headers=self.headers, **kwargs)

    def patch(self, *args, **kwargs):
        return requests.patch(*args, proxies=self.proxies, headers=self.headers, **kwargs)

    def delete(self, *args, **kwargs):
        return requests.delete(*args, proxies=self.proxies, headers=self.headers, **kwargs)

    def close(self):
        self.headers = None
        self.proxies = None

    def reset(self):
        self.headers['UserAgent'] = UserAgent().random

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


class TorClient(Client):

    def __init__(self, proxy_port=9050, ctrl_port=9051, password=None):
        self.proxy_port = proxy_port
        self.ctrl_port = ctrl_port
        super().__init__()
        self.ctrl = Controller.from_port(port=self.ctrl_port)
        self.ctrl.authenticate(password=password)
        self.ip_retrieval_sites = [
            'http://ipecho.net/plain',
            'https://ident.me',
        ]
        self.proxies = {
            'http': 'socks5://127.0.0.1:%d' % self.proxy_port,
            'https': 'socks5://127.0.0.1:%d' % self.proxy_port
        }

    def new_identity(self):
        print('[ ] Requesting new ip adress')
        self.ctrl.signal(stem.Signal.NEWNYM)
        time.sleep(self.ctrl.get_newnym_wait())
        print("[+] Changed IP to %s: " % self.get(random.choice(self.ip_retrieval_sites)).text)

    def close(self):
        self.ctrl.close()

    def reset(self):
        self.new_identity()
        self.headers['UserAgent'] = UserAgent().random
