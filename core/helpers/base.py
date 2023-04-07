import random
from rest_framework.renderers import JSONRenderer
from django.http.response import HttpResponse
from core.constants import RequestContentTypes

###### JSON API Response Helpers #######


class JSONResponse(HttpResponse):
    """
    An HttpResponse that renders its content into JSON.
    """

    def __init__(self, data: dict, **kwargs):
        content = JSONRenderer().render(data)
        kwargs["content_type"] = RequestContentTypes.APPLICATION_JSON
        super(JSONResponse, self).__init__(content, **kwargs)


class UnauthorizedJSONResponse(HttpResponse):
    """
    An HttpResponse that renders its content into JSON.
    Status code: 401 - Response for unauthorized access
    """

    def __init__(self, data: dict = None, message: str = None, **kwargs):
        payload = {"code": 401}
        if data:
            payload.update({"response": data})
        if message:
            payload.update({"message": message})
        content = JSONRenderer().render(payload)
        print(content)
        kwargs["content_type"] = RequestContentTypes.APPLICATION_JSON
        super(UnauthorizedJSONResponse, self).__init__(content, status=401, **kwargs)


class BadRequestJSONResponse(HttpResponse):
    """
    An HttpResponse that renders its content into JSON.
    Status code - 400, Response for bad request
    """

    def __init__(self, data: dict = None, message: str = None, status=400, **kwargs):
        payload = {"code": status}
        if data:
            payload.update({"response": data})
        if message:
            payload.update({"message": message})
        content = JSONRenderer().render(payload)
        print(content)
        kwargs["content_type"] = RequestContentTypes.APPLICATION_JSON
        super(BadRequestJSONResponse, self).__init__(content, status=status, **kwargs)


class NotFoundJSONResponse(HttpResponse):
    """
    An HttpResponse that renders its content into JSON.
    Status code - 404, Response for object not found
    """

    def __init__(
        self, data: dict = None, message: str = None, status_code=404, **kwargs
    ):
        payload = {"code": 404}
        if data:
            payload.update({"response": data})
        if message:
            payload.update({"message": message})
        content = JSONRenderer().render(payload)
        print(content)
        kwargs["content_type"] = RequestContentTypes.APPLICATION_JSON
        super(NotFoundJSONResponse, self).__init__(
            content, status=status_code, **kwargs
        )


class ForbiddenJSONResponse(HttpResponse):
    """
    An HttpResponse that renders its content into JSON.
    Status code - 403, Response for forbidden operation
    """

    def __init__(self, data: dict = None, message: str = None, **kwargs):
        payload = {"code": 403}
        if data:
            payload.update({"response": data})
        if message:
            payload.update({"message": message})
        content = JSONRenderer().render(payload)
        print(content)
        kwargs["content_type"] = RequestContentTypes.APPLICATION_JSON
        super(ForbiddenJSONResponse, self).__init__(content, status=403, **kwargs)


class ServerErrorJSONResponse(HttpResponse):
    """
    An HttpResponse that renders its content into JSON.
    Status code - 500, Response for internal server error
    """

    def __init__(self, data: dict = None, message: str = None, **kwargs):
        payload = {"code": 500}
        if data:
            payload.update({"response": data})
        if message:
            payload.update({"message": message})
        content = JSONRenderer().render(payload)
        print(content)
        kwargs["content_type"] = RequestContentTypes.APPLICATION_JSON
        super(ServerErrorJSONResponse, self).__init__(content, status=500, **kwargs)


class SuccessJSONResponse(HttpResponse):
    """
    An HttpResponse that renders its content into JSON.
    Status code - 200, Response for successful completion of request
    """

    def __init__(self, data=None, message=None, **kwargs):
        payload = {"code": 200}
        if data:
            payload.update({"response": data})
        if message:
            payload.update({"message": message})
        content = JSONRenderer().render(payload)
        print(content)
        kwargs["content_type"] = RequestContentTypes.APPLICATION_JSON
        super(SuccessJSONResponse, self).__init__(content, status=200, **kwargs)


class CustomErrorJSONResponse(HttpResponse):
    """
    An HttpResponse with custom code in response
    Status code - 400, Generic bad request response
    but with a custom error code passed in its response body.
    This code is extrated from the message
    """

    def __init__(self, data: dict = None, message: str = None, **kwargs):
        custom_status_code = 400
        try:
            custom_status_code, message = message.split("__", 1)
        except (ValueError, AttributeError):
            pass
        payload = {"code": int(custom_status_code)}
        if data:
            payload.update({"response": data})
        if message:
            payload.update({"message": message})
        content = JSONRenderer().render(payload)
        print(content)
        kwargs["content_type"] = RequestContentTypes.APPLICATION_JSON
        super(CustomErrorJSONResponse, self).__init__(content, status=400, **kwargs)


###### END JSON API Response Helpers #######


def random_string_generator(
    length: int = 10,
    digits: bool = True,
    alphabets: bool = False,
    special_characters: bool = False,
) -> str:
    """
    Generic function utility to generate Random Numbers and String
    Params:
        length -> length of the output string
        digits -> include digits?
        alphabets -> to include alphabets?
        special_characters -> to include special chars?
    Returns:
        randomly generated string
    """

    string = ""
    if digits:
        string += "0123456789"
    if alphabets:
        string += "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    if special_characters:
        string += "!@#$%^&*"
    return "".join([random.choice(string) for char in range(length)])
