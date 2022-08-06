import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


class DataSyncer:
    # loads sync and sensor data files into pandas dataframes. common methods for TX and RX
    def __init__(self, id, sync_log_path, sensor_log_path, num_sensors):

        self.__id = id
        self.__sync_log_path = sync_log_path
        self.__sensor_log_path = sensor_log_path
        self.__num_sensors = num_sensors

        self.__sync_datatype = [("framesElapsed", "f4"), ("msg", "f4")]
        self.__sensor_datatype = [
            ("framesElapsed", "f4"),
            *[("{}-x{}".format(self.id, str(i)), "f4") for i in range(1, self.num_sensors + 1)],
        ]

        # load TX raw data from log files
        self.__sync_raw = self.__loadBinaryData(self.__sync_log_path, self.__sync_datatype)
        self.__sensor_raw = self.__loadBinaryData(self.__sensor_log_path, self.__sensor_datatype)

        # load into pandas dataframe for easier manipulation
        self.__sync_df_raw = pd.DataFrame(self.__sync_raw).astype(int)
        self.__sensor_df = pd.DataFrame(self.__sensor_raw)

        self.__offsetSensorData()

    @property
    def id(self):
        return self.__id

    @property
    def sync_log_path(self):
        return self.__sync_log_path

    @property
    def sensor_log_path(self):
        return self.__sensor_log_path

    @property
    def num_sensors(self):
        return self.__num_sensors

    @property
    def sensor_raw(self):
        return self.__sensor_raw

    @property
    def sync_raw(self):
        return self.__sync_raw

    @property
    def sync_df_raw(self):
        return self.__sync_df_raw

    @property
    def sensor_df(self):
        return self.__sensor_df

    @sensor_df.setter  # needs a setter in order to update the sensor_df after sync
    def sensor_df(self, value):
        self.__sensor_df = value

    def __loadBinaryData(self, path, dtype):
        _ = np.fromfile(path, dtype=dtype)
        print('Loading "{}"...'.format(path))
        return _

    def __offsetSensorData(self):
        self.__sensor_df = self.sensor_df.iloc[self.sync_df_raw["framesElapsed"].iloc[0]:self.
                                               sync_df_raw["framesElapsed"].iloc[-1]].copy()
        print("Offsetting {} sensor data...".format(self.id))

    def plotSensorRaw(self):
        _, ax = plt.subplots()

        framesElapsed = [e[0] for e in self.sensor_raw]

        for j in range(1, self.num_sensors + 1):
            ax.plot(framesElapsed, [e[j] for e in self.sensor_raw], label="{}-x{}".format(self.id, str(j)))

        ax.set_title("Raw {} Sensor Data".format(self.id))
        ax.set_xlabel("Frames Elapsed")

        ax.legend(loc="upper left")

    def plotSensor(self):
        _, ax = plt.subplots()

        self.sensor_df.plot(y=[c for c in self.sensor_df.columns if c != "framesElapsed"], ax=ax, use_index=True)
        ax.set_title("Synced {} Sensor Data".format(self.id))
        ax.set_xlabel("Frames Elapsed")

        ax.legend(loc="upper left")

    def saveSyncedData(self, path):  # TODO
        pass


class DataSyncerTX(DataSyncer):

    def __init__(self, id, sync_log_path, sensor_log_path, num_sensors, d_clock=689 * 8 + 8):

        super(DataSyncerTX, self).__init__(id, sync_log_path, sensor_log_path, num_sensors)

        self.__d_clock = d_clock  # interval in frames at which the TX sends a clock signal

        self.sensor_df = self.sensor_df.drop('framesElapsed', axis=1).reset_index(drop=True)

    @property
    def d_clock(self):
        return self.__d_clock


class DataSyncerRX(DataSyncer):

    def __init__(self, id, sync_log_path, sensor_log_path, num_sensors):

        super(DataSyncerRX, self).__init__(id, sync_log_path, sensor_log_path, num_sensors)

        self.__synced_to_id = False

    @property
    def synced_to_id(self):
        return self.__synced_to_id

    @synced_to_id.setter  # needs a setter in order to update the synced_to_id after sync
    def synced_to_id(self, value):
        self.__synced_to_id = value

    def syncSensorData(self, TX_Syncer):

        print("Syncing {} sensor data against {}...".format(self.id, TX_Syncer.id))

        sensor_df_aux = self.sensor_df.copy()

        # check if messages are received at the same interval
        for i in range(len(self.sync_df_raw) - 1):  # iterate over received blocks

            diff = (self.sync_df_raw['framesElapsed'][i + 1] - self.sync_df_raw['framesElapsed'][i]) - TX_Syncer.d_clock

            if diff == 0:  # if spacing between received blocks equals d_clock, everything is fine
                continue

            if diff > 0:  # remove extra samples . if larger than one block, check if twice the block +-2 samples

                if diff > TX_Syncer.d_clock:  # if diff larger than d_clock, normalise difference
                    m = np.floor(diff / TX_Syncer.d_clock)
                    diff = diff - m * TX_Syncer.d_clock
                    if diff == 0:  # if difference is equal to n blocks, continue
                        continue

                for j in reversed(range(diff)):  # remove n extra samples
                    sensor_df_aux = sensor_df_aux.drop(index=(sensor_df_aux.loc[
                        self.sensor_df['framesElapsed'] == self.sync_df_raw['framesElapsed'][i + 1]].index - j)[0])

                print("Dropped {} extra samples from {} sensor data".format(diff, self.id))

            if diff < 0:

                # linear interpolation

                t2 = self.sync_df_raw['framesElapsed'][i + 1] + 1  # end of current +1
                t1 = self.sync_df_raw['framesElapsed'][i + 1]  # end of current
                x2 = sensor_df_aux.loc[t2, [
                    sensor_datatype[0] for sensor_datatype in self._DataSyncer__sensor_datatype[1:self.num_sensors + 1]
                ]].values  # get sensor values at t2
                x1 = sensor_df_aux.loc[t2, [
                    sensor_datatype[0] for sensor_datatype in self._DataSyncer__sensor_datatype[1:self.num_sensors + 1]
                ]].values  # get sensor values at t1

                m = (x2 - x1) / (t2 - t1)  # point-slope equation -> y = m(x-x0) + y0

                sensor_df_aux_top = sensor_df_aux.loc[:t1 + 1].copy()
                for i in range(1, abs(diff) + 1):
                    t = np.round(t1 + i * (t2 - t1) / (abs(diff) + 1), 7)
                    x = np.round(m * (t - t1) + x1, 7)
                    sensor_df_aux_top.loc[t1 + i] = [t, *x]  # now index is not equal to t anymore and t is irrelevant

                sensor_df_aux = pd.concat([sensor_df_aux_top,
                                           sensor_df_aux.loc[t2:]])  # concatenate sensor_df_aux_top and sensor_df_aux

                print("Added {} extra samples to {} sensor data".format(abs(diff), self.id))

        self.sensor_df = sensor_df_aux.drop('framesElapsed', axis=1).reset_index(drop=True)
        self.synced_to_id = TX_Syncer.id
