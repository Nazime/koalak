import functools
import inspect


def is_future_method(function):
    """Tell if this function will be a method based on if it's first argument is named 'self'"""
    # this function is used in "optionalargs"
    try:
        return inspect.getfullargspec(function).args[0] == "self"
    except IndexError:
        return False


def optionalargs(decorator_to_decorate, *, firstarg=None):
    # TODO: decorator as a class
    # TODO: yassmine: add option to disable "ismethod" guessing, and to tell that it's a method
    """Decorator for decorators to allow them to be called with or without
    arguments.

    Example:
        ```
        @optionalargs
        def decorator(obj, msg="Hello"):
            print(msg)
            return obj

        # Now the decorator can be called with or without arguments

        # without arguments:
        @decorator
        def f():
            pass

        # with arguments
        @decorator(msg="Good Bye")
        def f():
            pass
        ```
    optionalargs can be called with or without arguments.

    By default only keyword arguments are allowed for the decorated decorator
    to enable positional arguments you have to specify either the type of
    the first argument or the type of the decorated object (by the decorated
    decorator) to resolve ambiguity.



    Args:
        decorated: type of the expected decorated object (by the decorated decorator)
            to resolve ambiguity
        firstarg: type of the first argument of the decorated decorator to resolve
            ambiguity

    """

    obj_is_method = is_future_method(decorator_to_decorate)

    def _refactored(obj_or_arg, args, kwargs, self=None):
        pre_args = []
        if self is not None:  # this was if self and I took 3 hours to debug it!
            pre_args.append(self)

        # There are 3 possibility for the first argument
        #  None => decorator called with brackets =>
        if obj_or_arg is None or (
            firstarg is not None and isinstance(obj_or_arg, firstarg)
        ):

            # decorator called with brackets
            #  @decorateme()
            #  def f():
            #      pass
            # or:
            #  @decorateme(arg=value)
            #  def f():
            #      pass
            arg = obj_or_arg
            del obj_or_arg

            if arg is not None:
                args = (arg, *args)

            def decorator(obj):
                return decorator_to_decorate(*pre_args, obj, *args, **kwargs)

            return decorator
        else:
            # decorator called without braketcs. Example
            #  @decorateme
            #  def f():
            #      pass
            obj = obj_or_arg
            del obj_or_arg

            return decorator_to_decorate(*pre_args, obj)

    if obj_is_method:
        # if it's a method we must add self in the signature
        @functools.wraps(decorator_to_decorate)
        def decorated_decorate_me(self, obj_or_arg=None, *args, **kwargs):
            return _refactored(obj_or_arg, args, kwargs, self=self)

    else:

        @functools.wraps(decorator_to_decorate)
        def decorated_decorate_me(obj_or_arg=None, *args, **kwargs):
            return _refactored(obj_or_arg, args, kwargs)

    return decorated_decorate_me


# decorate optionalargs with itself
optionalargs = optionalargs(optionalargs)
