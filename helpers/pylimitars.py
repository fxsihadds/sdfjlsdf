from functools import wraps
from typing import Callable, Union
from pyrate_limiter import Duration, Rate, Limiter, BucketFullException

class Ratelimiter:
    def __init__(self) -> None:
        self.rate = Rate(10, Duration.MINUTE)
        self.limiter = Limiter(self.rate)

    async def acquire(self, user_id: Union[str, int]) -> bool:
        try:
            self.limiter.try_acquire(user_id)
            return False
        except BucketFullException as e:
            return True