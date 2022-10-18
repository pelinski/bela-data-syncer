import numpy as np


def SyncedDataLoader(path, id, num_sensors):
    loaded = np.fromfile(path, dtype=[*[("{}-x{}".format(id, str(i)), "f4")
                                        for i in range(1, num_sensors + 1)], ])
    return np.array([list(row) for row in loaded])
