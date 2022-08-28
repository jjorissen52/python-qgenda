import inspect
import functools


@functools.cache
def get_default_args(func):
    signature = inspect.signature(func)
    return {
        k: v.default
        for k, v in signature.parameters.items()
        if v.default is not inspect.Parameter.empty
    }


@functools.cache
def get_arg_names(method):
    """
    Returns any explicitly named positional or keyword arguments defined in
    the function signature.
    """
    return method.__code__.co_varnames[:method.__code__.co_argcount]


def named_method_params(method, args, kwargs):
    """
    Takes a method and its arguments and return a dictionary of all values that will be
    passed to it. This allows for easy inspection.
    """
    args_names = get_arg_names(method)
    params = get_default_args(method)
    args_dict = {**dict(zip(args_names, args)), **kwargs}
    params.update(args_dict)
    params.pop('self', None)
    return params
