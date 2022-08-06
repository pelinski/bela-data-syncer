import unittest
import numpy as np

from DataSyncer import DataSyncerTX, DataSyncerRX


class checkTX(unittest.TestCase):

    def test_checkTxSyncInterval(self):

        # load sync and sensor data from Bela master (TX)
        dataSyncerTX = DataSyncerTX(
            id="TX0",
            sync_log_path="DataSyncer/test-data/TX0-sync.log",
            sensor_log_path="DataSyncer/test-data/TX0-data.log",
            num_sensors=3,
            d_clock=689 * 8 + 8,
        )

        # check that the sync messages are sent in a d_clock interval
        diff = []
        for i in range(len(dataSyncerTX.sync_df_raw) - 1):
            diff.append((dataSyncerTX.sync_df_raw["framesElapsed"].iloc[i + 1] -
                         dataSyncerTX.sync_df_raw["framesElapsed"].iloc[i]) - dataSyncerTX.d_clock)

        self.assertEqual(
            np.count_nonzero(diff),
            0,
            "Clock signals in TX are not sent in d_clock intervals.",
        )


class checkRX(unittest.TestCase):

    def test_checkRxLengthInSamples(self):

        # load sync and sensor data from Bela master (TX)
        dataSyncerTX = DataSyncerTX(
            id="TX0",
            sync_log_path="DataSyncer/test-data/TX0-sync.log",
            sensor_log_path="DataSyncer/test-data/TX0-data.log",
            num_sensors=4,
            d_clock=689 * 8 + 8,
        )

        # load sync and sensor data from Bela receivers (RX)
        dataSyncerRX1 = DataSyncerRX(id="RX1",
                                     sync_log_path="DataSyncer/test-data/RX1-sync.log",
                                     sensor_log_path="DataSyncer/test-data/RX1-data.log",
                                     num_sensors=4)
        dataSyncerRX2 = DataSyncerRX(id="RX2",
                                     sync_log_path="DataSyncer/test-data/RX2-sync.log",
                                     sensor_log_path="DataSyncer/test-data/RX2-data.log",
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


# TODO add tests for interpolation

if __name__ == '__main__':
    unittest.main(verbosity=2)
    exit()
