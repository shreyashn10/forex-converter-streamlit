import requests


class ApiError(Exception):
    """Raised when an API request fails or returns an unusable response."""


def get_json(url, params=None, timeout=10):
    """Send a GET request and return the parsed JSON response.

    Args:
        url (str): The endpoint to call.
        params (dict, optional): Query string parameters to send.
        timeout (int): Request timeout in seconds.

    Returns:
        dict: The parsed JSON response body.

    Raises:
        ApiError: If the request cannot be made (e.g. no internet
            connection, timeout), the API returns a non-200 status
            code, or the response body is not valid JSON.
    """
    try:
        response = requests.get(url, params=params, timeout=timeout)
    except requests.exceptions.RequestException as error:
        raise ApiError(f"Could not reach the API: {error}") from error

    if response.status_code != 200:
        raise ApiError(
            f"API request failed with status code {response.status_code}."
        )

    try:
        return response.json()
    except ValueError as error:
        raise ApiError("API response was not valid JSON.") from error
