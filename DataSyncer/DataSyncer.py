# Data, DataSyncerTX and DataSyncerRX classes

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


class Data:
    # Data class, parent class for DataSyncerTX and DataSyncerRX

    def __init__(self, id, num_sensors, sensor_log_path,  sync_log_path=None, sample_rate=None, verbose=True):

        self.__id = id  # Bela id. TX0 for transmitter/master and RX0, RX1, ... for receivers/slaves
        # number of sensors connected to the Bela analog ports
        self.__num_sensors = num_sensors
        self.__sensor_log_path = sensor_log_path  # path to sensor log file
        self.__sync_log_path = sync_log_path  # path to sync log file
        self.__isMulti = False if self.sync_log_path is None else True
        self.__sample_rate = sample_rate  # analog sample rate of the Bela
        self.__verbose = verbose  # print info messages

        self.__sync_datatype = None if not self.__isMulti else [("framesElapsed", "f4"),
                                                                ("msg", "f4")]  # datatype for sync data (necessary for loading binary files)

        self.__sensor_raw_datatype = [
            ("framesElapsed", "f4"),
            *[("{}-x{}".format(self.id, str(i)), "f4")
              for i in range(1, self.num_sensors + 1)],
        ]  # datatype for sensor data (necessary for loading binary files)

        # Load TX raw data from log files
        self.__sync_raw = None if not self.__isMulti else self.loadBinaryData(
            self.__sync_log_path, self.__sync_datatype)
        self.__sensor_raw = self.loadBinaryData(
            self.__sensor_log_path, self.__sensor_raw_datatype)

        # Load the raw data into pandas dataframes for easier manipulation
        self.__sync_df_raw = None if not self.__isMulti else pd.DataFrame(
            self.__sync_raw).astype(int)
        self.__sensor_df = pd.DataFrame(self.__sensor_raw)

        if self.__isMulti:
            # Remove sensor data recorded before the first and after the last sync message
            self.__offsetSensorData()
        else:
            self.sensor_df = self.sensor_df.drop(
                'framesElapsed', axis=1).reset_index(drop=True)

    # Property getters
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

    @property
    def sensor_np(self):
        return self.__sensor_df.to_numpy()
    
    @property
    def sample_rate(self):
        return self.__sample_rate

    @property
    def verbose(self):
        return self.__verbose

    # Property setters
    @sensor_df.setter  # needs a setter in order to update the sensor_df after sync
    def sensor_df(self, value):
        self.__sensor_df = value

    @verbose.setter
    def verbose(self, value):
        self.__verbose = value

    def __offsetSensorData(self):
        # Remove sensor data recorded before the first and after the last sync message
        self.__sensor_df = self.sensor_df.iloc[self.sync_df_raw["framesElapsed"].iloc[0]:self.
                                               sync_df_raw["framesElapsed"].iloc[-1]].copy()
        if self.verbose:
            print("Offsetting {} sensor data...".format(self.id))

    def plotSensorRaw(self):
        # Plot each sensor raw signal over framesElapsed
        _, ax = plt.subplots()

        # framesElapsed is the first item of each row
        framesElapsed = [e[0] for e in self.sensor_raw]
        
        if self.sample_rate:
            timeElapsed = [e / self.sample_rate for e in framesElapsed] # time elapsed
            x = timeElapsed
            x_label = "Time Elapsed (s)"
        else:
            x = framesElapsed 
            x_label = "Frames Elapsed"


        for j in range(1, self.num_sensors + 1):
            ax.plot(x, [
                    e[j] for e in self.sensor_raw], label="{}-x{}".format(self.id, str(j)))

        ax.set_title("Raw {} Sensor Data".format(self.id))
        ax.set_xlabel(x_label)

        ax.legend(loc="upper left")
        
        return ax

    def plotSensor(self):
        
        # Plot each sensor raw signal over framesElapsed
        _, ax = plt.subplots()

        # framesElapsed is now the index of each row
        framesElapsed = np.arange(self.sensor_df.shape[0])

        if self.sample_rate:
            timeElapsed = [e / self.sample_rate for e in framesElapsed] 
            x = timeElapsed
            x_label = "Time Elapsed (s)"
        else:
            x = framesElapsed 
            x_label = "Frames Elapsed"

        ax.plot(x, self.sensor_df, label=self.sensor_df.columns)

        ax.set_title("Synced {} Sensor Data".format(self.id))
        ax.set_xlabel(x_label)

        ax.legend(loc="upper left")
        
        return ax

    def loadBinaryData(self, path, dtype):
        # Load binary data from log file, given data type
        if self.verbose:
            print('Loading "{}"...'.format(path))

        _ = np.fromfile(path, dtype=dtype)

        return _

    def saveSyncedData(self, filepath):
        # Save synced sensor data to binary file
        f = open(filepath, 'w+b')
        binary_format = bytearray(self.sensor_np)
        f.write(binary_format)
        f.close()


class DataSyncerTX(Data):
    # DataSyncerTX, class for transmitter/master Bela

    def __init__(self, id, sync_log_path, sensor_log_path, num_sensors, d_clock=689 * 8 + 8, sample_rate=None, verbose=True):

        super(DataSyncerTX, self).__init__(
            id=id, sync_log_path=sync_log_path, sensor_log_path=sensor_log_path, num_sensors=num_sensors, sample_rate=sample_rate,verbose=verbose)

        self.__d_clock = d_clock  # interval in frames at which the TX sends a clock signal

        # framesElapsed is dropped from the processed sensor data since after interpolation/dropping in the RX signals there appear decimal or missing framesElapsed values, so the raw/recorded framesElapsed value is dropped and the row index is used instead
        self.sensor_df = self.sensor_df.drop(
            'framesElapsed', axis=1).reset_index(drop=True)

    # Property getters
    @property
    def d_clock(self):
        return self.__d_clock


class DataSyncerRX(Data):
    # DataSyncerRX, class for receiver/slave Bela

    def __init__(self, id, sync_log_path, sensor_log_path, num_sensors, sample_rate=None, verbose=True):

        super(DataSyncerRX, self).__init__(
            id=id, sync_log_path=sync_log_path, sensor_log_path=sensor_log_path, num_sensors=num_sensors, sample_rate=sample_rate,verbose=verbose)

        # whether the receiver has been synced to a transmitter, False or takes string value of transmitter id
        self.__synced_to_id = False

    # Property getters
    @property
    def synced_to_id(self):
        return self.__synced_to_id

    # Property setters
    @synced_to_id.setter  # needs a setter in order to update the synced_to_id after sync
    def synced_to_id(self, value):
        self.__synced_to_id = value

    def syncSensorData(self, TX_Syncer):
        # Syncs sensor data to a transmitter's (TX_Syncer) clock signal. This means (1) the frames index in the RX and in the TX are equivalent, so (2) between each clock signal, a constant number of frames (d_clock) have elapsed, and hence (3) if there are frames missing in the RX between two clock signals, the signal values are interpolated or (4) if there are extra frames in the RX between two clock signals, those extra frames are dropped.

        if self.verbose:
            print("Syncing {} sensor data against {}...".format(
                self.id, TX_Syncer.id))

        # To keep the reference frames index, we do the interpolation/dropping on sensor_df_aux and then copy the values back to sensor_df
        sensor_df_aux = self.sensor_df.copy()

        # Iterate over each block of frames between clock signals
        for i in range(len(self.sync_df_raw) - 1):  # i refers to the raw data

            # Number of frames elapsed between two clock signals
            diff = (self.sync_df_raw['framesElapsed'][i + 1] -
                    self.sync_df_raw['framesElapsed'][i]) - TX_Syncer.d_clock

            # If diff==0, the number of frames elapsed between two clock signals is equal to the TX's d_clock, so no interpolation/dropping is needed
            if diff == 0:
                continue

            # If diff>0, there are extra frames in the RX between two clock signals, so we need to drop those extra frames
            if diff > 0:

                # Check if the number of frames of extra frames is larger than d_clock. If this is the case, the RX might have missed a clock signal, but as long as the next clock signal is received in a multiple of d_clock frames, there's no need for interpolation/dropping.
                if diff > TX_Syncer.d_clock:
                    # 'Unwrap' the difference to the nearest multiple of d_clock
                    m = np.floor(diff / TX_Syncer.d_clock)
                    diff = diff - m * TX_Syncer.d_clock
                    if diff == 0:  # If the unwrapped difference is equal to 0, the number of frames elapsed is a multiple of d_clock and no interpolation/dropping is needed. Otherwise, continue to drop the extra frames
                        continue

                # TODO case in which extraframes are more than half of d_clock --> throw error

                # Drop extra frames
                for j in reversed(range(diff)):
                    sensor_df_aux = sensor_df_aux.drop(index=(sensor_df_aux.loc[
                        self.sensor_df['framesElapsed'] == self.sync_df_raw['framesElapsed'][i + 1]].index - j)[0])

                if self.verbose:
                    print("Dropped {} extra samples from {} sensor data".format(
                        diff, self.id))

            # If diff<0, there are frames missing in the RX between two clock signals, so we need to interpolate those missing frames
            if diff < 0:

                # TODO if more than half of the block is missing, throw error

                # Linear interpolation
                # end of current block +1
                t2 = self.sync_df_raw['framesElapsed'][i + 1] + 1
                # end of current block
                t1 = self.sync_df_raw['framesElapsed'][i + 1]
                x2 = sensor_df_aux.loc[t2, [
                    sensor_datatype[0] for sensor_datatype in self._Data__sensor_raw_datatype[1:self.num_sensors + 1]
                ]].values  # get sensor values at t2
                x1 = sensor_df_aux.loc[t2, [
                    sensor_datatype[0] for sensor_datatype in self._Data__sensor_raw_datatype[1:self.num_sensors + 1]
                ]].values  # get sensor values at t1

                m = (x2 - x1) / (t2 - t1)  # slope of linear interpolation

                # Copy the values of the dataframe up until t1 (before the interpolated values)
                sensor_df_aux_top = sensor_df_aux.loc[:t1 + 1].copy()

                # Add interpolated values to the end of sensor_df_aux_top
                for i in range(1, abs(diff) + 1):
                    t = np.round(
                        t1 + i * (t2 - t1) / (abs(diff) + 1), 7
                    )  # those t (or frameElapsed in the dataframe) values are now decimal and hence do not correspond to the frameElapsed index anymore
                    x = np.round(m * (t - t1) + x1, 7)
                    sensor_df_aux_top.loc[t1 + i] = [t, *x]

                # Merges sensor_df_aux_top (sensor values up until t2, the end of the interpolation) with the rest of the dataframe (sensor data values after t2)
                sensor_df_aux = pd.concat([sensor_df_aux_top,
                                           sensor_df_aux.loc[t2:]])  # concatenate sensor_df_aux_top and sensor_df_aux

                if self.verbose:
                    print("Added {} extra samples to {} sensor data".format(
                        abs(diff), self.id))

        # framesElapsed is dropped from the processed sensor data since after interpolation/dropping in the RX signals there appear decimal or missing framesElapsed values, so the raw/recorded framesElapsed value is dropped and the row index is used instead
        self.sensor_df = sensor_df_aux.drop(
            'framesElapsed', axis=1).reset_index(drop=True)

        # Value of synced_to_id is updated with the transmitter (TX_Syncer) id
        self.synced_to_id = TX_Syncer.id
