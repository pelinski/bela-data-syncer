import numpy as np


class SyncedDataLoader:
    def __init__(self, id, path, num_sensors):

        self.__id = id
        self.__path = path
        self.__num_sensors = num_sensors
        self.__loaded_data = self.__load_data()

    @property
    def id(self):
        return self.__id

    @property
    def path(self):
        return self.__path

    @property
    def num_sensors(self):
        return self.__num_sensors

    @property
    def loaded_data(self):
        return self.__loaded_data

    def __load_data(self):
        loaded = np.fromfile(self.path, dtype=[*[("{}-x{}".format(self.id, str(i)), "f4")
                                            for i in range(1, self.num_sensors + 1)], ])
        return np.array([list(row) for row in loaded])
