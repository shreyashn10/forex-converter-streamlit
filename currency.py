def convert_amount(amount, rate):
    """Convert an amount from one currency to another."""
    return amount * rate


def calculate_inverse_rate(rate):
    """Calculate the inverse of a conversion rate."""
    if rate == 0:
        return 0.0
    return 1 / rate


def format_conversion_result(
    on_date, from_currency, to_currency, rate, amount, converted_amount
):
    """Build the result sentence shown to the user.

    Amounts are rounded to 2 decimal places and rates to 4 decimal
    places, which keeps the message readable and consistent
    regardless of how many decimals the API returns.

    Args:
        on_date (str): The date the rate applies to.
        from_currency (str): Source currency code.
        to_currency (str): Destination currency code.
        rate (float): Conversion rate from from_currency to to_currency.
        amount (float): The amount entered by the user.
        converted_amount (float): The converted amount.

    Returns:
        str: A sentence describing the conversion, in the format
            required by the assignment brief.
    """
    inverse_rate = calculate_inverse_rate(rate)
    return (
        f"The conversion rate on {on_date} from {from_currency} to "
        f"{to_currency} was {round(rate, 4)}. So {round(amount, 2)} in "
        f"{from_currency} correspond to {round(converted_amount, 2)} in "
        f"{to_currency}. The inverse rate was {round(inverse_rate, 4)}."
    )
