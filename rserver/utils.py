from asyncio import Lock

class LazyAsyncLock():
    def __init__(self):
        self._lock = None

    @property
    def lock(self):
        if not self._lock:
            self._lock = Lock()
        return self._lock

