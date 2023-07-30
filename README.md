# Options Advisor

[![Coverage Status](https://coveralls.io/repos/github/d-lopes/options-advisor/badge.svg?branch=main)](https://coveralls.io/github/d-lopes/options-advisor?branch=main) [![Known Vulnerabilities](https://snyk.io/test/github/d-lopes/options-advisor/badge.svg)](<https://snyk.io/test/github/d-lopes/options-advisor>) [![License](https://img.shields.io/badge/license-MPL--2.0-blue.svg)](https://mozilla.org/MPL/2.0)

Python Repo for tasks concerning management and selection of stock options @ NYSE

## Getting Started

### prerequisites

- python 3.11 must be installed
- the dependencies from the `./requirements.txt` must be installed via pip
    => run this command from command line within the root directory of this repo: `pip3 install -r requirements.txt`

### using command line

adjust the parameters in the top of `./src/main/run.py`:

```python
symbols = ['BAC']
mode = analyzer.Types.PUT
default_filter = analyzer.Filter.getDefaults()
default_filter.max_strike = 40
start_week_offset = 3
end_week_offset = start_week_offset + 4
```

run this command from command line within the root directory of this repo: `python3 -m src.main.run`

### using Web UI

tbd

### using docker

tbd

## How to test?

simply run `python3 -m unittest` from the root directory

see answer to following stack overflow article for further info: <https://stackoverflow.com/questions/1896918/running-unittest-with-typical-test-directory-structure>
