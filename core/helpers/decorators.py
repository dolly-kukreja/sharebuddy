import logging
import functools
from core.helpers.base import ServerErrorJSONResponse

LOGGER = logging.getLogger(__name__)


def handle_unknown_exception(
    logger=None,
    return_value=(False, "SOMETHING_WENT_WRONG"),
    log_level="exception",
    print_=False,
    raise_again=False,
):

    if not logger:
        logger = LOGGER

    def _func_decorator(func):
        @functools.wraps(func)
        def _func_wrapper(*args, **kwargs):

            try:
                return func(*args, **kwargs)
            except Exception as error:
                title_message = f"{log_level.upper()} in {func.__name__}:"
                if print_:
                    print(title_message)
                    print(error)

                getattr(logger, log_level)(error)

                if raise_again:
                    raise error

                return return_value

        return _func_wrapper

    return _func_decorator


def handle_unknown_exception_api_view(logger, print_=False):

    log_level = "exception"
    return_value = ServerErrorJSONResponse("SOMETHING_WENT_WRONG")

    def _func_decorator(func):
        @functools.wraps(func)
        def _func_wrapper(*args, **kwargs):

            try:
                return func(*args, **kwargs)
            except Exception as error:
                title_message = f"{log_level.upper()} in {func.__name__}:"
                if print_:
                    print(title_message)
                    print(error)

                getattr(logger, log_level)(error)

                return return_value

        return _func_wrapper

    return _func_decorator
