"""
TODO
"""

from .base import route_permutations, hashable_list
from depend_test_framework.log import get_logger

LOGGER = get_logger(__name__)

try:
    from .DL import LSTM
except ImportError:
    LOGGER.error("Cannot import deep learning algorithms, need install tensorflow")
    LSTM = None
