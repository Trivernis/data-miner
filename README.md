# data-miner

A tool to periodically collect data from api endpoints and store them inside a folder.
**Please ensure that you are allowed to use the api this way before using this tool!**

## Prerequisites

You need to have python 3.8 or higher and pipenv installed.

## Install

```shell script
pipenv install
```

## Usage

```
usage: miner.py [-h] [-t] -o OUTPUT_DIR [-i INTERVAL] [-m METHOD] [-p PAYLOAD_FILE] url

Periodically mine data

positional arguments:
  url                   the data endpoint url

optional arguments:
  -h, --help            show this help message and exit
  -t, --tor             If tor should be used for requests
  -o OUTPUT_DIR, --output-dir OUTPUT_DIR
                        The output directory for the data
  -i INTERVAL, --interval INTERVAL
                        The interval in which the data is requested
  -m METHOD, --method METHOD
                        The HTTP method that is used
  -p PAYLOAD_FILE, --payload-file PAYLOAD_FILE
                        The file containing the requests payload.
```

## License

GPL-3.0