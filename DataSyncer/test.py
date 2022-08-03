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
            dClock=689 * 8 + 8,
        )

        # check that the sync messages are sent in a dClock interval
        diffTx = []

        for i in range(len(dataSyncerTX.sync_df) - 1):
            # the indexes in syncTx refer to dfTx (corrected has altered indexes)
            diffTx.append((dataSyncerTX.sync_df["framesElapsed"].iloc[i + 1] -
                           dataSyncerTX.sync_df["framesElapsed"].iloc[i]) -
                          dataSyncerTX.dClock)

        self.assertEqual(
            np.count_nonzero(diffTx),
            0,
            "Clock signals in TX are not sent in dClock intervals.",
        )


class checkRX(unittest.TestCase):

    def test_checkRxLengthInSamples(self):
        dataSyncerTX = DataSyncerTX(
            id="TX0",
            sync_log_path="DataSyncer/test-data/TX0-sync.log",
            sensor_log_path="DataSyncer/test-data/TX0-data.log",
            num_sensors=3,
            dClock=689 * 8 + 8,
        )

        dataSyncerRX = DataSyncerRX(
            id="RX1",
            sync_log_path="DataSyncer/test-data/RX1-sync.log",
            sensor_log_path="DataSyncer/test-data/RX1-data.log",
            num_sensors=4)

        dataSyncerRX.syncSensorData(dataSyncerTX)

        self.assertEqual(
            len(dataSyncerRX.sensor_df) == len(dataSyncerTX.sensor_df), True,
            "RX sensor data length is not equal to TX sensor data length.")


if __name__ == '__main__':
    unittest.main()
    exit()
