# bela_data_syncer

Python library to sync sensor data recorded in various Belas with the [bela-data-logger](https://github.com/pelinski/bela-data-logger) pipeline.

## Install

```
pip install "git+https://github.com/pelinski/bela-data-syncer.git#egg=bela-data-syncer"
```

## Development building and testing

```
git clone https://github.com/pelinski/bela-data-syncer.git
pipenv install -d
```

## todo

- throw error if samples to drop are > half of a block + write test for this
