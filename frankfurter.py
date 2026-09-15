"""frankfurter.py

Functions for talking to the Frankfurter currency API
(https://www.frankfurter.app/). Each function calls one endpoint and
pulls out the values the rest of the app needs. The actual HTTP work
is done by api.py.
"""

from datetime import date

from api import ApiError, get_json

BASE_URL = "https://api.frankfurter.app"


def get_currencies():
    """Retrieve the available currency codes and their names.

    Returns:
        dict: Mapping of currency code to currency name, e.g.
            {"AUD": "Australian Dollar", "USD": "United States Dollar"}.

    Raises:
        ApiError: If the currency list cannot be retrieved.
    """
    data = get_json(f"{BASE_URL}/currencies")
    if not isinstance(data, dict) or not data:
        raise ApiError("No currency data was returned by the API.")
    return data


def get_latest_rate(from_currency, to_currency):
    """Retrieve the latest conversion rate between two currencies.

    Args:
        from_currency (str): Currency code to convert from, e.g. "AUD".
        to_currency (str): Currency code to convert to, e.g. "USD".

    Returns:
        tuple: (rate, rate_date) where rate is a float and rate_date
            is the date (as a string) the rate applies to.

    Raises:
        ApiError: If the rate cannot be retrieved.
    """
    if from_currency == to_currency:
        return 1.0, date.today().isoformat()

    params = {"from": from_currency, "to": to_currency}
    data = get_json(f"{BASE_URL}/latest", params=params)
    return _extract_rate(data, to_currency)


def get_historical_rate(from_currency, to_currency, on_date):
    """Retrieve the conversion rate for a specific past date.

    Args:
        from_currency (str): Currency code to convert from.
        to_currency (str): Currency code to convert to.
        on_date (str or datetime.date): The date to look up, e.g.
            "2023-07-10" or a date object.

    Returns:
        tuple: (rate, rate_date).

    Raises:
        ApiError: If the date is in the future or the rate cannot be
            retrieved.
    """
    if isinstance(on_date, date):
        on_date = on_date.isoformat()

    if on_date > date.today().isoformat():
        raise ApiError("The selected date cannot be in the future.")

    if from_currency == to_currency:
        return 1.0, on_date

    params = {"from": from_currency, "to": to_currency}
    data = get_json(f"{BASE_URL}/{on_date}", params=params)
    return _extract_rate(data, to_currency)


def _extract_rate(data, to_currency):
    """Pull the rate and date out of a Frankfurter API response.

    Args:
        data (dict): Parsed JSON response from /latest or a historical
            date endpoint.
        to_currency (str): The currency code the rate should be for.

    Returns:
        tuple: (rate, rate_date).

    Raises:
        ApiError: If the expected fields are missing from the response.
    """
    rates = data.get("rates") if isinstance(data, dict) else None
    rate = rates.get(to_currency) if isinstance(rates, dict) else None
    rate_date = data.get("date") if isinstance(data, dict) else None

    if rate is None or rate_date is None:
        raise ApiError(f"No rate data was returned for {to_currency}.")

    return float(rate), rate_date
