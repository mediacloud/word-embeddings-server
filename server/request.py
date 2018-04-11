import logging
from flask import request, jsonify
from functools import wraps

logger = logging.getLogger(__name__)


def json_error_response(message, status_code=400):
    response = jsonify({
        'status': status_code,
        'message': message,
    })
    response.status_code = status_code
    return response


def validate_params_exist(form, params):
    for param in params:
        if param not in form:
            raise ValueError('Missing required value for '+param)


def form_fields_required(*expected_form_fields):
    # Handy decorator for ensuring that the form has the fields you need
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                logger.debug(request.form)
                validate_params_exist(request.form, expected_form_fields)
                return func(*args, **kwargs)
            except ValueError as e:
                logger.exception("Missing a required form field")
                return json_error_response(e.args[0])
        return wrapper
    return decorator
