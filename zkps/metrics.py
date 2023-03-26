from collections import defaultdict


class Counter:
    call_count = defaultdict(int)

    def __init__(self, func):
        self.func = func

    def __call__(self, *args, **kwargs):
        Counter.call_count[self.func.__name__] += 1
        return self.func(*args, **kwargs)

    @classmethod
    def display(cls):
        for func_name, count in Counter.call_count.items():
            print(f"Function '{func_name}' has been called {count} times")

    @classmethod
    def reset(cls):
        Counter.call_count.clear()
