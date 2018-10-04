import json
import time


from qgenda.api.exceptions import HTTPError, APICallError


def handle_error_response(logger):
    def real_decorator(client_obj, response):
        """
        Raises HTTPError if there is an HTTP error and raise_errors=True, otherwise just adds error information to
        response.text
        """
        raise_errors = client_obj.raise_errors
        if response.status_code >= 400:
            logger.error(f'API Call returned HTTP error response {response.status_code}: {response.reason}')
            if raise_errors:
                raise HTTPError(f'API Call returned HTTP error response {response.status_code}: {response.reason}')
            else:
                setattr(response, 'text', {
                    "error": response.status_code,
                    "error_description": response.reason,
                })
        else:
            response_dict = json.loads(response.text)
            if any(["error" in key for key in response_dict]) and raise_errors:
                raise APICallError(f'Error Response: {json.dumps(response_dict, indent=2)}')
        return client_obj, response
    return real_decorator


def handle_login_response(client_obj, response):
    """
    For now just sets auth_details on the caller, but will eventually handle caching
    """
    request_start = time.time()
    response_dict = json.loads(response.text)
    if "expires_in" in response_dict:
        expiration_time = request_start + int(response_dict["expires_in"]) - 30  # 30 second buffer here to be safe
        response_dict.update({"expiration_time": expiration_time})
    client_obj.auth_details = response_dict
    return client_obj, response
