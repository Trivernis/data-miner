import requests
from torrequest import TorRequest
from fake_useragent import UserAgent


class Client:

    def __init__(self):
        self.session = requests.Session()
        self.session.headers['UserAgent'] = UserAgent().random

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
        return self.session.get(*args, **kwargs)

    def post(self, *args, **kwargs):
        return self.session.get(*args, **kwargs)

    def put(self, *args, **kwargs):
        return self.session.put(*args, **kwargs)

    def patch(self, *args, **kwargs):
        return self.session.patch(*args, **kwargs)

    def delete(self,*args, **kwargs):
        return self.session.delete(*args, **kwargs)

    def close(self):
        self.session.close()

    def reset(self):
        self.session.headers['UserAgent'] = UserAgent().random
        self.session.cookies.clear()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


class TorClient(Client):

    def __init__(self, *args, **kwargs):
        super().__init__()
        self.tr = TorRequest(*args, **kwargs)
        self.tr.session.headers['UserAgent'] = UserAgent().random
        self.session = self.tr

    def new_identity(self):
        self.tr.reset_identity()
        print("[+] Changed IP to %s: " % self.get('https://ident.me').text)

    def reset(self):
        self.new_identity()
        self.tr.session.cookies.clear()
        self.tr.session.headers['UserAgent'] = UserAgent().random
