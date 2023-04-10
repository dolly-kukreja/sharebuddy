import logging
import functools
from core.helpers.base import ForbiddenJSONResponse, ServerErrorJSONResponse
from core.helpers.query_search import get_or_none
from core.models import Address

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


def validate_user_details():
    def _method_wrapper(view_function):
        def validate_user_permissions(request, *args, **kwargs):
            user = request.user
            if not user.is_mobile_number_verified or not user.is_email_verified:
                return ForbiddenJSONResponse("Please verify email and mobile details.")

            address_object = get_or_none(Address, user=user)
            if not address_object:
                return ForbiddenJSONResponse("Please update your address details.")

            return view_function(request, *args, **kwargs)

        return validate_user_permissions

    return _method_wrapper
