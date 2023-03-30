from collections import defaultdict
import functools


class Counter:
    call_count = defaultdict(int)

    def __init__(self, func):
        self.func = func
        functools.update_wrapper(self, func)

    def __call__(self, *args, **kwargs):
        Counter.call_count[self.func.__qualname__] += 1
        return self.func(*args, **kwargs)

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return functools.partial(self, instance)

    @classmethod
    def display(cls):
        for func_name, count in Counter.call_count.items():
            print(f"Function '{func_name}' has been called {count} times")

    @classmethod
    def reset(cls):
        Counter.call_count.clear()
