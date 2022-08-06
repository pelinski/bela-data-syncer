import unittest
import numpy as np

from DataSyncer import DataSyncerTX, DataSyncerRX


class checkTX(unittest.TestCase):

    def test_checkTxSyncInterval(self):
        dataSyncerTX = DataSyncerTX(
            id="TX0",
            sync_log_path="DataSyncer/test-data/TX0-sync.log",
            sensor_log_path="DataSyncer/test-data/TX0-data.log",
            num_sensors=3,
            d_clock=689 * 8 + 8,
        )

        # check that the sync messages are sent in a d_clock interval
        diffTx = []

        for i in range(len(dataSyncerTX.sync_df) - 1):
            # the indexes in syncTx refer to dfTx (corrected has altered indexes)
            diffTx.append((dataSyncerTX.sync_df["framesElapsed"].iloc[i + 1] -
                           dataSyncerTX.sync_df["framesElapsed"].iloc[i]) - dataSyncerTX.d_clock)

        self.assertEqual(
            np.count_nonzero(diffTx),
            0,
            "Clock signals in TX are not sent in d_clock intervals.",
        )


class checkRX(unittest.TestCase):

    def test_checkRxLengthInSamples(self):
        dataSyncerTX = DataSyncerTX(
            id="TX0",
            sync_log_path="DataSyncer/test-data/TX0-sync.log",
            sensor_log_path="DataSyncer/test-data/TX0-data.log",
            num_sensors=3,
            d_clock=689 * 8 + 8,
        )

        dataSyncerRX1 = DataSyncerRX(id="RX2",
                                     sync_log_path="DataSyncer/test-data/RX2-sync.log",
                                     sensor_log_path="DataSyncer/test-data/RX2-data.log",
                                     num_sensors=4)

        dataSyncerRX2 = DataSyncerRX(id="RX2",
                                     sync_log_path="DataSyncer/test-data/RX2-sync.log",
                                     sensor_log_path="DataSyncer/test-data/RX2-data.log",
                                     num_sensors=4)

        dataSyncerRX1.syncSensorData(dataSyncerTX)
        dataSyncerRX2.syncSensorData(dataSyncerTX)

        self.assertEqual(
            len(dataSyncerRX1.sensor_df) == len(dataSyncerTX.sensor_df), True,
            "RX1 sensor data length is not equal to TX sensor data length.")

        self.assertEqual(
            len(dataSyncerRX2.sensor_df) == len(dataSyncerTX.sensor_df), True,
            "RX2 sensor data length is not equal to TX sensor data length.")


if __name__ == '__main__':
    unittest.main(verbosity=2)
    exit()
