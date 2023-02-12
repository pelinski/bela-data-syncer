# 2 – Dataset processing (host)

Once the log files from step 1 have been transferred to the host machine, we can align the signals framewise using the `DataSyncer` library. You can follow the `2-host_data-processing.ipynb` notebook or install the library and incorporate it into your data processing workflow.

### Use the notebook:
In order to use the notebook you will need a python environment with a few packages installed. You can install it using (in the host terminal):

```
pipenv install
```
and you can open the notebook by using:
```
pipenv run jupyter notebook
```


### Or install the library
Alternatively, you can install the library and add it to your data processing workflow:
```
pip install "git+https://github.com/pelinski/bela-data-syncer.git#egg=bela-data-syncer"
```
