import pandas as pd
import numpy as np


class DataSyncerTX():
    def __init__(self,
                 TX_sync_log_path: str,
                 TX_sensor_log_path: str,
                 TX_num_sensors: int,
                 dClock: int = 689*8 + 8):

        self.__dClock = dClock  # interval in frames at which the TX sends a clock signal

        self.__TX_sync_log_path = TX_sync_log_path
        self.__TX_sensor_log_path = TX_sensor_log_path
        self.__TX_num_sensors = TX_num_sensors

        # load TX raw data from log files
        self.__TX_sync_raw = self.__loadBinaryData(self.__TX_sync_log_path, [(
            'framesElapsed', 'f4'), ('msg', 'f4')])
        self.__TX_sensor_raw = self.__loadBinaryData(self.__TX_sensor_log_path, [(
            'framesElapsed', 'f4'), *[('TX-x'+str(i), 'f4') for i in range(1, self.__TX_num_sensors+1)]])

        # load into pandas dataframe for easier manipulation
        self.__TX_sync_df = pd.DataFrame(self.__TX_sync_raw)
        self.__TX_sensor_df = pd.DataFrame(self.__TX_sensor_raw)

        self.__processTxSensorData()

    @property
    def TX_sync_log_path(self) -> str:
        return self.__TX_sync_log_path

    @property
    def TX_sensor_log_path(self) -> str:
        return self.__TX_sensor_log_path

    @property
    def TX_num_sensors(self) -> int:
        return self.__TX_num_sensors

    @property
    def TX_sync_raw(self) -> np.array:
        return self.__TX_sync_raw

    @property
    def TX_sync_df(self) -> pd.DataFrame:
        return self.__TX_sync_df

    @property
    def dClock(self) -> int:
        return self.__dClock

    def __loadBinaryData(self, path: str,  dtype: list) -> np.array:
        _ = np.fromfile(path, dtype=dtype)
        print('Loaded "{}".'.format(path))
        return _

    def __processTxSensorData(self) -> None:
        # signal starts at the first message sent and ends at the last message sent
        self.__TX_sensor_df = self.__TX_sensor_df.iloc[self.__TX_sync_df['t']
                                                       [0]: self.__TX_sync_df['t'].iloc[-1]].copy()
        print('Processed TX sensor data.')

    def checkTxSyncConsistency(self) -> None:
        # check that the sync messages are sent in a dClock interval
        diffTx = []

        for i in range(len(self.__TX_sensor_df)-1):
            # the indexes in syncTx refer to dfTx (corrected has altered indexes)
            diffTx.append(
                (self.__TX_sensor_df['t'][i+1] - self.__TX_sensor_df['t'][i]))

        print(diffTx)  # TODO error message

    def saveCorrectedTxData(self, path: str) -> None:
        pass  # save as numpy array binary file


class DataSyncerRX():
    pass
