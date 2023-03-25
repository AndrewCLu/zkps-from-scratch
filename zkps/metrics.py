from collections import defaultdict

def counter(func):
    call_count = defaultdict(int)

    def wrapper(*args, **kwargs):
        call_count[func.__name__] += 1
        print(f"Function '{func.__name__}' has been called {call_count[func.__name__]} times")
        return func(*args, **kwargs)

    wrapper.call_count = lambda: call_count

    return wrapper
