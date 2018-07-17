import timeit


class ResourceWatcher(object):
    def __init__(self):
        self._start_time = None
        self._end_time = None

    def __enter__(self):
        self._start_time = timeit.default_timer()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._end_time = timeit.default_timer()

    @property
    def run_time(self):
        return self._end_time - self._start_time
