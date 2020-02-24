#!/bin/env python3.8
import argparse
from lib.client import TorClient, Client
from lib.utils import parse_duration
from lib.io import FileManager
from requests import ConnectionError
from requests.exceptions import SSLError
import time
import os
import mimetypes
import base64
import hashlib
import json
import random


def get_folder_name(url: str) -> str:
    m = hashlib.sha256()
    m.update(url.encode('utf-8'))
    return base64.urlsafe_b64encode(m.digest()).decode('utf-8')


def parse_arguments():
    parser = argparse.ArgumentParser(description='Periodically mine data')
    parser.add_argument('url', type=str, help='the data endpoint url', nargs='+')
    parser.add_argument('-t', '--tor', action='store_true', help='If tor should be used for requests')
    parser.add_argument('-o', '--output-dir', default='data', type=str, help='The output directory for the data')
    parser.add_argument('-i', '--interval', default='1h', type=str, help='The interval in which the data is requested')
    parser.add_argument('-m', '--method', default='GET', type=str, help='The HTTP method that is used')
    parser.add_argument('-b', '--body', type=str, help='The file containing the requests payload/body.')
    parser.add_argument('-p', '--tor-password', type=str, help='The password used for the tor control port.')
    parser.add_argument('-z', '--compress', action='store_true', help='If the data should be compressed')
    parser.add_argument('--no-verify', action='store_true', help='Skips the verification of ssl certificates')
    return parser.parse_args()


def request_loop(client: Client, urls: [str], fm: FileManager, method: str = 'GET', verify=True, interval=1800, body=None):
    random_factor = round(interval/10)
    names = {}
    for url in urls:
        names[url] = get_folder_name(url)
        status_fname = os.path.join(fm.data_dir, '%s-status.csv' % names[url])
        if not os.path.exists(status_fname):
            with open(status_fname, 'w') as f:
                f.write('datetime,status-code,timing\n')
    while True:
        try:
            for url in urls:
                d = names[url]
                status_file = open(os.path.join(fm.data_dir, '%s-status.csv' % d), 'a')
                try:
                    req = client.request(url, method=method, data=body, verify=verify)
                    if req.status_code == 200:
                        content_type = 'text/plain'
                        if 'content-type' in req.headers.keys():
                            content_type = req.headers['content-type'].split(';')[0]
                        extension = mimetypes.guess_extension(content_type)
                        print('[+] Request to %s succeeded: mime: %s, timing: %ss' %
                              (url, content_type, req.elapsed.total_seconds()))
                        f_name = time.strftime('%d-%m-%y_%H-%M-%S') + extension
                        with fm.get_file(d, f_name) as f:
                            f.write(req.text)
                        fm.store_file(d, f_name)
                        print('[+] Successfully stored response data as %s ' % f_name)
                    else:
                        print('[-] Request failed with code %s: %s' % (req.status_code, req.text))
                    status_file.write('%s,%s,%s\n' % (time.strftime('%d.%m.%y_%H:%M:%S'), req.status_code, req.elapsed.total_seconds()))
                except SSLError:
                    print('There is a problem with the certificate of %s' % url)
                    print('To ignore that please pass the --no-verify flag')
                except ConnectionError as e:
                    print('Failed to connect to %s: %s' % (url, e))
                    status_file.write('%s,0,0\n' % time.strftime('%d.%m.%y_%H:%M:%S'))
                status_file.close()
            client.reset()
            pause_duration = interval + random.randint(-random_factor, random_factor)
            print('[ ] Pausing for %ss' % pause_duration)
            time.sleep(pause_duration)
        except KeyboardInterrupt:
            client.close()
            return


def main():
    print('--- Data Miner by Trivernis ---')
    print('(Please respect the api providers)')
    print('-------------------------------')
    args = parse_arguments()
    interval = parse_duration(args.interval)
    if interval.total_seconds() == 0:
        print("[-] The interval must be greater than one second (this is not a dos tool).")
        exit(1)
    if args.tor:
        client = TorClient(password=args.tor_password)
    else:
        client = Client()
    if not os.path.exists(args.output_dir):
        os.mkdir(args.output_dir)
    mapping = {}
    mapping_file = '%s/mapping.json' % args.output_dir
    if os.path.exists(mapping_file):
        with open(mapping_file, 'r') as mf:
            try:
                mapping = json.load(mf)
            except Exception as e:
                print(e)
    dirs = []
    for url in args.url:
        folder_name = get_folder_name(url)
        mapping[url] = folder_name
        dirs.append(folder_name)
    with open(mapping_file, 'w') as mf:
        json.dump(mapping, mf, indent='  ')
    body = None
    if args.body:
        body = open(args.body, 'rb')
    fm = FileManager(args.output_dir, dirs, compress=args.compress)
    print('[ ] Starting request loop...')
    request_loop(client, args.url, fm, args.method, not args.no_verify, int(interval.total_seconds()), body=body)


if __name__ == '__main__':
    main()
