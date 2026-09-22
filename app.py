from datetime import date, timedelta

import pandas as pd
import streamlit as st

from api import ApiError
from frankfurter import (
    get_currencies,
    get_historical_rate,
    get_latest_rate,
    get_time_series,
)
from currency import convert_amount, format_conversion_result

# How far back the "Rate Trend" chart looks, in days (last 3 years).
TREND_PERIOD_DAYS = 3 * 365

st.title("FX Converter")


@st.cache_data(ttl=3600)
def load_currencies():
    """Fetch the list of available currencies, cached for an hour."""
    return get_currencies()


# The currency list only needs to be fetched once per session (it
# rarely changes), so the app stops early with a clear error if it
# cannot be loaded at all.
try:
    currencies = load_currencies()
except ApiError as error:
    st.error(f"Could not load the list of currencies: {error}")
    st.stop()

currency_codes = sorted(currencies.keys())


def currency_label(code):
    """Show a currency code together with its name in select boxes."""
    return f"{code} - {currencies[code]}"


def default_index(code, fallback=0):
    """Find the index of a currency code, or fall back if not found."""
    return currency_codes.index(code) if code in currency_codes else fallback


amount = st.number_input(
    "Enter the amount to be converted:", min_value=0.0, value=100.0, step=1.0
)

from_currency = st.selectbox(
    "From currency:",
    currency_codes,
    index=default_index("AUD"),
    format_func=currency_label,
)

to_currency = st.selectbox(
    "To currency:",
    currency_codes,
    index=default_index("USD"),
    format_func=currency_label,
)


def display_conversion(rate, rate_date):
    """Calculate and show the conversion result for a fetched rate."""
    converted_amount = convert_amount(amount, rate)
    message = format_conversion_result(
        rate_date, from_currency, to_currency, rate, amount, converted_amount
    )
    st.text(message)


def display_rate_trend():
    """Show a line chart of the rate over roughly the last 3 years."""
    if from_currency == to_currency:
        return

    end_date = date.today()
    start_date = end_date - timedelta(days=TREND_PERIOD_DAYS)

    try:
        series = get_time_series(from_currency, to_currency, start_date, end_date)
    except ApiError as error:
        st.warning(f"Could not load the rate trend chart: {error}")
        return

    if not series:
        return

    chart_data = pd.Series(series, name="Rate")
    chart_data.index = pd.to_datetime(chart_data.index)
    chart_data = chart_data.sort_index()

    st.subheader("Rate Trend Over the Last 3 years")
    st.line_chart(chart_data)


st.subheader("Latest Conversion Rate")

if st.button("Get Latest Rate"):
    if amount <= 0:
        st.warning("Enter an amount greater than 0 to see a conversion.")
    else:
        try:
            rate, rate_date = get_latest_rate(from_currency, to_currency)
            display_conversion(rate, rate_date)
            display_rate_trend()
        except ApiError as error:
            st.error(f"Could not get the latest conversion rate: {error}")

st.subheader("Historical Conversion Rate")

historical_date = st.date_input(
    "Select a date for historical rates:",
    value=date.today(),
    max_value=date.today(),
)

if st.button("Get Historical Rate"):
    if amount <= 0:
        st.warning("Enter an amount greater than 0 to see a conversion.")
    else:
        try:
            rate, rate_date = get_historical_rate(
                from_currency, to_currency, historical_date
            )
            display_conversion(rate, rate_date)
        except ApiError as error:
            st.error(f"Could not get the historical conversion rate: {error}")
