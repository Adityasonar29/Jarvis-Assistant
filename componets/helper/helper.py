from functools import wraps

# Add a run_once decorator function
def run_once(func):
    """
    A decorator that ensures a function is executed only once.
    
    Usage:
    @run_once
    def my_function():
        # This code will run only once
        print("This will only print once")
    """
    has_run = False
    result = None
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        nonlocal has_run, result
        if not has_run:
            result = func(*args, **kwargs)
            has_run = True
            return result
        else:
            return result
    
    return wrapper