# Options Advisor

[![codecov](https://codecov.io/github/d-lopes/options-tracker-input/branch/main/graph/badge.svg?token=TSZDGJ2Q8G)](https://codecov.io/github/d-lopes/options-tracker-input)

[![Known Vulnerabilities](https://snyk.io/test/github/d-lopes/options-tracker-input/badge.svg)](<https://snyk.io/test/github/d-lopes/options-tracker-input>)

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
