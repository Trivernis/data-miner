#!/bin/env python3.8
import argparse
from lib.client import TorClient, Client
from lib.utils import parse_duration
import time
import os
import mimetypes
import base64
import hashlib
import json


def get_folder_name(url: str) -> str:
    m = hashlib.sha256()
    m.update(url.encode('utf-8'))
    return base64.urlsafe_b64encode(m.digest()).decode('utf-8')


def parse_arguments():
    parser = argparse.ArgumentParser(description='Periodically mine data')
    parser.add_argument('url', type=str, help='the data endpoint url', nargs='+')
    parser.add_argument('-t', '--tor', action='store_true', help='If tor should be used for requests')
    parser.add_argument('-o', '--output-dir', required=True, type=str, help='The output directory for the data')
    parser.add_argument('-i', '--interval', default='1h', type=str, help='The interval in which the data is requested')
    parser.add_argument('-m', '--method', default='GET', type=str, help='The HTTP method that is used')
    parser.add_argument('-p', '--payload-file', type=str, help='The file containing the requests payload.')
    return parser.parse_args()


def request_loop(client: Client, urls: [str], out_dir: str, method: str = 'GET', interval=1800, body=None):
    while True:
        try:
            for url in urls:
                req = client.request(url, method=method, data=body)
                if req.status_code == 200:
                    extension = mimetypes.guess_extension(req.headers['content-type'].split(';')[0])
                    print('[+] Request to %s succeeded: mime: %s, timing: %ss' %
                          (url, req.headers['content-type'], req.elapsed.total_seconds()))
                    with open('%s/%s/%s%s' % (out_dir, get_folder_name(url),
                                              time.strftime('%m-%d-%y_%H-%M-%S'), extension), 'w') as f:
                        f.write(req.text)
                else:
                    print('[-] Request failed with code %s: %s' % (req.status_code, req.text))
            client.reset()
            print('[ ] Pausing for %ss' % interval)
            time.sleep(interval)
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
        client = TorClient()
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
    for url in args.url:
        folder_name = get_folder_name(url)
        folder_path = '%s/%s' % (args.output_dir, folder_name)
        mapping[url] = folder_name
        if not os.path.exists(folder_path):
            os.mkdir(folder_path)
    with open(mapping_file, 'w') as mf:
        json.dump(mapping, mf, indent='  ')
    body = None
    if args.payload_file:
        body = open(args.payload_file, 'rb')
    print('[ ] Starting request loop...')
    request_loop(client, args.url, args.output_dir, args.method, int(interval.total_seconds()), body=body)


if __name__ == '__main__':
    main()
