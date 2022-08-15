# bela_data_syncer

Python library to sync sensor data recorded in various Belas with the bela-parallel-comm library.

## Install

```
pip install "git+https://github.com/pelinski/bela-data-syncer.git#egg=bela-data-syncer"
```

## Development build and testing

```
git clone https://github.com/pelinski/bela-data-syncer.git
pipenv install -d
```

## todo

- rewrite example
- throw error if samples to drop are > half of a block + test for this
