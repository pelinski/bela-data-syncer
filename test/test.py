# DataSyncer testing

import unittest
import os
import numpy as np

from DataSyncer import DataSyncerTX, DataSyncerRX, Data, SyncedDataLoader


class test_TX(unittest.TestCase):

    def test_TxSyncInterval(self):

        # load sync and sensor data from Bela master (TX)
        dataSyncerTX = DataSyncerTX(
            id="TX0",
            sync_log_path="test/data/TX0-sync.log",
            sensor_log_path="test/data/TX0-data.log",
            num_sensors=4,
            d_clock=689 * 8 + 8,
        )

        # check that the sync messages are sent in a d_clock interval
        diff = []
        for i in range(len(dataSyncerTX.sync_df_raw) - 1):
            diff.append(
                (dataSyncerTX.sync_df_raw["framesElapsed"].iloc[i + 1] -
                 dataSyncerTX.sync_df_raw["framesElapsed"].iloc[i]) -
                dataSyncerTX.d_clock)

        self.assertEqual(
            np.count_nonzero(diff),
            0,
            "Clock signals in TX are not sent in d_clock intervals.",
        )


class test_RX(unittest.TestCase):

    def test_RxLengthInSamples(self):

        # load sync and sensor data from Bela master (TX)
        dataSyncerTX = DataSyncerTX(
            id="TX0",
            sync_log_path="test/data/TX0-sync.log",
            sensor_log_path="test/data/TX0-data.log",
            num_sensors=4,
            d_clock=689 * 8 + 8,
        )

        # load sync and sensor data from Bela receivers (RX)
        dataSyncerRX1 = DataSyncerRX(id="RX1",
                                     sync_log_path="test/data/RX1-sync.log",
                                     sensor_log_path="test/data/RX1-data.log",
                                     num_sensors=4)
        dataSyncerRX2 = DataSyncerRX(
            id="RX2",
            # load tweaked data for interpolation testing
            sync_log_path="test/data/RX2-sync-int.log",
            sensor_log_path="test/data/RX2-data.log",
            num_sensors=4)

        # sync sensor data from RXs to TX
        dataSyncerRX1.syncSensorData(dataSyncerTX)
        dataSyncerRX2.syncSensorData(dataSyncerTX)

        # check if RXs sensor data has the same length in samples as TX sensor data
        self.assertEqual(
            len(dataSyncerRX1.sensor_df) == len(dataSyncerTX.sensor_df), True,
            "RX1 sensor data length is not equal to TX sensor data length.")

        self.assertEqual(
            len(dataSyncerRX2.sensor_df) == len(dataSyncerTX.sensor_df), True,
            "RX2 sensor data length is not equal to TX sensor data length.")

        self.assertEqual(
            len(dataSyncerRX1.sensor_df) % dataSyncerTX.d_clock == 0, True,
            "RX1 sensor data length is not a multiple of d_clock.")

        self.assertEqual(
            len(dataSyncerRX2.sensor_df) % dataSyncerTX.d_clock == 0, True,
            "RX2 sensor data length is not a multiple of d_clock.")


class test_DataLoader(unittest.TestCase):

    def test_DataLoaderShapes(self):

        id = "RX1"
        num_sensors = 4

        # load sync and sensor data from Bela master (TX)
        dataSyncerTX = DataSyncerTX(
            id=id,
            sync_log_path="test/data/{}-sync.log".format(id),
            sensor_log_path="test/data/{}-data.log".format(id),
            num_sensors=num_sensors,
            d_clock=689 * 8 + 8,
        )

        # temporary file to store the generated sensor data type
        test_fn = "test/data-syncer.tmp"

        # save synced data
        dataSyncerTX.saveSyncedData(test_fn)

        # load synced data
        sensor_data = SyncedDataLoader(
            id=id, path=test_fn, num_sensors=num_sensors)

        os.remove(test_fn)

        self.assertEqual(
            dataSyncerTX.sensor_np.shape == sensor_data.shape, True,
            "Saved data should be equal to loaded data.",
        )


class test_MonoData(unittest.TestCase):

    def test_DataLoaderShapes(self):

        id = "RX0"
        num_sensors = 2

        # load sync and sensor data from Bela master (TX)
        dataSyncerTX = Data(
            id=id,
            sensor_log_path="test/data/mono/{}-data.log".format(id),
            num_sensors=num_sensors,
        )

        # temporary file to store the generated sensor data type
        test_fn = "test/data-mono.tmp"

        # save synced data
        dataSyncerTX.saveSyncedData(test_fn)

        # load synced data
        sensor_data = SyncedDataLoader(
            id=id, path=test_fn, num_sensors=num_sensors)

        os.remove(test_fn)

        self.assertEqual(
            dataSyncerTX.sensor_np.shape == sensor_data.shape, True,
            "Saved data should be equal to loaded data.",
        )

# TODO test error case in which there are more than half of the block missing values in the sensor data


if __name__ == '__main__':
    unittest.main(verbosity=2)
    exit()
