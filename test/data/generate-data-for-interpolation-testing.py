# shift sync data to test DataSyncerRX interpolation method

import numpy as np

# datatype
dt = np.dtype([('t', 'f4'), ('msg', 'f4')])

# load raw sync data
syncDataRx = np.fromfile('RX2-sync.log', dtype=dt)

# shift sync data so that difference between consecutive received clock signals is less than dClock and the interpolation method can be tested
syncDataRx[10][0] = syncDataRx[10][0] - 1
syncDataRx[20][0] = syncDataRx[20][0] - 2
syncDataRx[30][0] = syncDataRx[30][0] - 1

# save altered sync data
f = open('RX2-sync-int.log', 'w+b')
binary_format = bytearray(syncDataRx)
f.write(binary_format)
f.close()
