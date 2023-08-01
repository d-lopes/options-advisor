# Options Advisor

[![Coverage Status](https://coveralls.io/repos/github/d-lopes/options-advisor/badge.svg?branch=main)](https://coveralls.io/github/d-lopes/options-advisor?branch=main) [![Known Vulnerabilities](https://snyk.io/test/github/d-lopes/options-advisor/badge.svg)](<https://snyk.io/test/github/d-lopes/options-advisor>) [![License](https://img.shields.io/badge/license-MPL--2.0-blue.svg)](https://mozilla.org/MPL/2.0)

Python Repo for tasks concerning management and selection of stock options @ NYSE

## Getting Started

### prerequisites

- python 3.11 must be installed
- the dependencies from the `./requirements.txt` must be installed via pip
    => run this command from command line within the root directory of this repo: `pip3 install -r requirements.txt`

### using command line

run this command from command line within the root directory of this repo: `python3 -m src.run -h`

```console
usage: run.py [-h] [-mode MODE] [-strike MAX_STRIKE] [-mp MIN_PUTS] [-mc MIN_CALLS] [-my MIN_YIELD] [-swo START_WEEK_OFFSET] [-ewo END_WEEK_OFFSET]

gathers data about stock options

options:
  -h, --help            show this help message and exit
  -mode MODE            PUT or CALL
  -strike MAX_STRIKE    filter for maximum acceptable strike
  -mp MIN_PUTS          filter for minium available puts
  -mc MIN_CALLS         filter for minium available calls
  -my MIN_YIELD         filter for minimum acceptable yield
  -swo START_WEEK_OFFSET
                        Offset from current week to start searching for expiry dates
  -ewo END_WEEK_OFFSET  Offset from current week to end searching for expiry dates
```

### using Web UI

tbd

### using docker

tbd

## How to test?

simply run `coverage run -m pytest` from the root directory

see answer to following stack overflow article for further info: <https://stackoverflow.com/questions/1896918/running-unittest-with-typical-test-directory-structure>
