"""
Learning the importance of the test case
"""

import numpy as np
import random
import pickle

from .log import get_logger
from .algorithms import LSTM

LOGGER = get_logger(__name__)


class StepsSeqScorer(object):
    def __init__(self, max_score, data_file='/tmp/data.save', algorithm=None,
                 func_map=None, time_steps=20):
        self.func_map = func_map
        self._time_steps = time_steps
        self._y_size = max_score + 1
        self._x_size = len(self.func_map)
        self._algorithm = algorithm or LSTM
        if not self._algorithm:
            raise Exception("Cannot find any valid algorithm for use")

        self._data_file = data_file
        if not algorithm:
            self._algorithm = LSTM(self._x_size, self._time_steps, self._y_size)
        else:
            self._algorithm = algorithm

    def dump_datas(self):
        self._algorithm.save(self._data_file)

    def load_datas(self):
        self._algorithm.restore(self._data_file)

    def train(self, data_set, dump_data=True):
        """
        args:
            data_set: list of (seq_list, value)
        """
        self._algorithm.train(self._transfer_data(data_set))
        if dump_data:
            self.dump_datas()

    def run(self, data, load_data=True):
        if load_data:
            self.load_datas()
        score = self._algorithm.run(self._transfer_input(data))
        return score

    def test(self, test_data, load_data=True):
        if load_data:
            self.load_datas()
        acc = self._algorithm.test(self._transfer_data(test_data))
        LOGGER.info("Accuracy: %s", acc)

    def _transfer_data(self, org_data):
        for func_seq, score in org_data:
            arr_x = self._transfer_input(func_seq)
            arr_y = np.zeros((1, self._y_size))
            arr_y[0][score] = 1
            yield arr_x, arr_y

    def _transfer_input(self, input_data):
        ret_arr = None
        for func in input_data:
            x = np.zeros((1, self._x_size))
            x[0][self.func_map[func]] = 1
            if ret_arr is None:
                ret_arr = x
            else:
                ret_arr = np.append(ret_arr, x, axis=0)
        # TODO: this make all input have the same length
        if len(ret_arr) > self._time_steps:
            raise Exception("This array size %d is bigger than %d" % (len(ret_arr), self._time_steps))
        while len(ret_arr) < self._time_steps:
            x = np.zeros((1, self._x_size))
            ret_arr = np.append(ret_arr, x, axis=0)
        return ret_arr

    def train_and_test(self, data_set):
        # random.seed(123)
        train_num = int(len(data_set) / 2)
        train_set = random.sample(data_set, train_num)
        self.train(train_set)
        test_num = int(len(data_set) / 5)
        self.test(random.sample(data_set, test_num), load_data=False)
