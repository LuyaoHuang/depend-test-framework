"""
TODO
"""

from base import route_permutations, hashable_list

try:
    from DL import LSTM
except ImportError:
    LOGGER.info("Cannot import deep learning algorithms, need install tensorflow")
    LSTM = None
