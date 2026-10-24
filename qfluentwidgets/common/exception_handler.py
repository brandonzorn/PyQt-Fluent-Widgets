from copy import deepcopy
from typing import Any, Callable


def exceptionHandler(*default: Any) -> Callable:
    """decorator for exception handling

    Parameters
    ----------
    *default:
        the default value returned when an exception occurs
    """

    def outer(func: Callable) -> Callable:

        def inner(*args: Any, **kwargs: Any) -> Any:
            try:
                return func(*args, **kwargs)
            except BaseException:
                value = deepcopy(default)
                if len(value) == 0:
                    return None
                if len(value) == 1:
                    return value[0]

                return value

        return inner

    return outer
