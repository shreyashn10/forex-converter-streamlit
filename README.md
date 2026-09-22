# FX Converter

## Author

- **Full Name:** Shreyash Narayane
- **Student ID:** 25934391
- **Subject:** Data Science Practice (DSP) : Assignment 2, Building a Currency Converter in Python

## Description

FX Converter is a Streamlit web app that converts an amount between two
currencies using live exchange-rate data from the
[Frankfurter API](https://www.frankfurter.app/), a free, open-source
foreign exchange rates API.

The app lets the user:

- Enter an amount to convert.
- Choose a source currency and a destination currency from the full list
  of currencies supported by Frankfurter (fetched from the API, not
  hard-coded).
- Click **Get Latest Rate** to see today's conversion rate, the converted
  amount, the inverse rate, and a line chart of that rate's trend over
  roughly the last 3 years.
- Pick a past date and click **Get Historical Rate** to see the conversion
  rate that applied on that date instead.

Both results are shown in the same sentence format, for example:

> The conversion rate on 2023-07-10 from AUD to BGN was 118.62. So 100.0 in AUD correspond to 11862.0 in BGN. The inverse rate was 0.0084.

The code is split into four modules so that each one has a single, clear
responsibility: `app.py` (interface), `api.py` (generic HTTP handling),
`frankfurter.py` (Frankfurter-specific API calls) and `currency.py`
(calculations and text formatting). This separation means, for example,
that the app could be pointed at a different exchange-rate API in future
by only rewriting `frankfurter.py`, without touching the interface or the
calculation logic.

### Challenges faced

- **Handling a same-currency conversion.** The Frankfurter API leaves the
  base currency out of its `rates` object, so requesting, say, AUD → AUD
  returns an empty `rates` dictionary rather than `{"AUD": 1.0}`. This
  would have been read as "missing rate data" and shown an error. It is
  handled by detecting `from_currency == to_currency` in `frankfurter.py`
  and returning a rate of `1.0` directly, without calling the API at all.
- **Deciding how much to round.** The assignment brief's own example
  sentences round rates inconsistently (e.g. `0.64246` vs `118.62`). A
  fixed rounding rule (4 decimal places for rates, 2 for amounts) was
  chosen in `currency.py` so the output text is predictable and readable
  no matter how many decimal places the API returns.
- **Keeping API failures from crashing the app.** Network errors, timeouts,
  non-200 responses, and malformed JSON are all different exceptions from
  the `requests` library. `api.py` catches all of them and re-raises a
  single custom `ApiError`, so `app.py` only ever has to catch one
  exception type and show a friendly `st.error()` message instead of a
  stack trace.
- **Testing without network access.** The Frankfurter API could not be
  reached from the environment this project was built in (outbound
  network access was blocked). To still verify the logic, the API
  responses were mocked with realistic sample JSON (matching the shapes
  documented at frankfurter.app/docs) so `frankfurter.py` and
  `currency.py` could be tested end-to-end offline. See "Testing
  Performed" at the end of this document for the full list of cases
  covered this way.

### Future improvements

- Add a "swap currencies" button to quickly reverse the From/To selection.
- Cache historical results per currency pair and date so repeated lookups
  don't re-call the API.
- Validate that the amount field rejects negative numbers at the input
  level (currently handled with `min_value=0.0`, but a custom message
  could be clearer than Streamlit's default).
- Add automated unit tests (e.g. with `pytest`) instead of the standalone
  mocked test script used during development, so tests can be run with a
  single `pytest` command.

## How To Setup

### Requirements

- **Python:** 3.9 or later (developed and tested with Python 3.10.12)
- **pip:** for installing dependencies

### Dependencies

| Package | Version used | Purpose |
|---|---|---|
| [`streamlit`](https://streamlit.io/) | 1.63.0 | Builds the web app interface |
| [`requests`](https://docs.python-requests.org/) | 2.34.2 | Makes HTTP GET requests to the Frankfurter API |
| [`pandas`](https://pandas.pydata.org/) | 2.3.3 | Shapes the historical rate series for the trend chart (`st.line_chart`) |

`pandas` is already installed automatically as a dependency of
`streamlit`, so no extra install step is needed beyond the command below.
Newer minor versions of all three packages should also work, since the
app only uses stable, long-standing features of each (`st.number_input`,
`st.selectbox`, `st.date_input`, `st.button`, `st.cache_data`,
`st.line_chart`, `requests.get`, and `pandas.Series`).

### Setup steps

1. Make sure Python 3.9+ is installed:

   ```bash
   python3 --version
   ```

2. (Optional but recommended) create and activate a virtual environment,
   so the project's dependencies don't affect other Python projects on
   your machine:

   ```bash
   python3 -m venv venv
   source venv/bin/activate      # on Windows: venv\Scripts\activate
   ```

3. Install the two dependencies, either individually:

   ```bash
   pip install streamlit==1.63.0 requests==2.34.2 pandas==2.3.3
   ```

   or without pinning versions (installs the latest compatible ones):

   ```bash
   pip install streamlit requests pandas
   ```

4. Confirm the install worked:

   ```bash
   streamlit --version
   ```

## How To Run The Program

1. Open a terminal and navigate to the folder containing `app.py`,
   `api.py`, `frankfurter.py`, `currency.py` and `README.md` (all five
   files must be in the same folder).

2. Run:

   ```bash
   streamlit run app.py
   ```

3. Streamlit will start a local web server and print a URL, e.g.:

   ```
   Local URL: http://localhost:8501
   ```

   It should also open automatically in your default browser. If it
   doesn't, copy the URL into your browser manually.

4. Using the app:
   - Enter an amount in the **"Enter the amount to be converted"** field.
   - Choose a **From currency** and a **To currency** from the dropdowns
     (these are populated live from the Frankfurter API when the app
     starts).
   - Click **Get Latest Rate** to see the current conversion rate, the
     converted amount, and the inverse rate, displayed as a sentence
     below the button, followed by a "Rate Trend Over the Last 3 years"
     line chart for that currency pair.
   - To check a past rate instead, pick a date using the **date picker**
     (dates after today are disabled) and click **Get Historical Rate**.
     The result appears below that button in the same sentence format.

5. To stop the app, go back to the terminal and press `Ctrl+C`.

6. **Requires an internet connection.** If the Frankfurter API cannot be
   reached, the app shows a red error message (instead of crashing)
   explaining that the currency list or rate could not be fetched.

## Project Structure

```
fx-converter/
├── app.py            # Streamlit interface: inputs, buttons, results, errors
├── api.py            # Generic HTTP GET helper and the ApiError exception
├── frankfurter.py    # Frankfurter API calls (currencies, latest, historical)
├── currency.py       # Conversion math, inverse rate, and message formatting
└── README.md         # This file
```

### `api.py` - generic API access

Contains one function and one exception, reused by `frankfurter.py`:

- **`get_json(url, params=None, timeout=10)`** - Sends a GET request to
  `url` with optional query parameters and a timeout, and returns the
  parsed JSON response body as a Python dictionary. Raises `ApiError` if
  the request cannot be completed (e.g. no internet connection or
  timeout), the response status code is not `200`, or the response body
  is not valid JSON.
- **`ApiError`** - A custom exception used across the whole project for
  any API-related failure, so calling code only needs to catch one
  exception type instead of several different `requests` exceptions.

### `frankfurter.py` - Frankfurter-specific logic

Uses `get_json()` from `api.py` to call four Frankfurter endpoints:

- **`get_currencies()`** - Calls `GET /currencies` and returns a
  dictionary mapping currency codes to full names, e.g.
  `{"AUD": "Australian Dollar", "USD": "United States Dollar", ...}`.
  Raises `ApiError` if the response is empty or not a dictionary.
- **`get_latest_rate(from_currency, to_currency)`** - Calls
  `GET /latest?from=<from_currency>&to=<to_currency>` and returns a tuple
  `(rate, date)`. If `from_currency` and `to_currency` are the same, it
  returns `(1.0, today's date)` without calling the API, since Frankfurter
  does not include the base currency in its own rates list.
- **`get_historical_rate(from_currency, to_currency, on_date)`** - Calls
  `GET /<on_date>?from=<from_currency>&to=<to_currency>` and returns
  `(rate, date)` for that specific day. Raises `ApiError` if `on_date` is
  later than today. Also short-circuits to `(1.0, on_date)` for a
  same-currency selection.
- **`get_time_series(from_currency, to_currency, start_date, end_date)`**
  - Calls `GET /<start_date>..<end_date>?from=<from_currency>&to=<to_currency>`
  and returns a dictionary mapping each date in the range to its rate,
  e.g. `{"2023-01-02": 0.68, "2023-01-03": 0.681, ...}`. Used to draw the
  "Rate Trend" chart. Returns an empty dictionary for a same-currency
  pair (the rate would be a flat `1.0` for every day, which isn't a
  useful chart).
- **`_extract_rate(data, to_currency)`** - A private helper shared by
  `get_latest_rate()` and `get_historical_rate()`. Safely reads the
  `rates` and `date` fields out of the raw JSON response and raises
  `ApiError` with a clear message if either is missing (for example, if
  `to_currency` is not a valid code).

### `currency.py` - calculations and formatting

Pure functions with no API calls, so they are simple to read and test in
isolation:

- **`convert_amount(amount, rate)`** - Returns `amount * rate`.
- **`calculate_inverse_rate(rate)`** - Returns `1 / rate`, or `0.0` if
  `rate` is exactly `0`, to avoid a `ZeroDivisionError`.
- **`format_conversion_result(on_date, from_currency, to_currency, rate, amount, converted_amount)`**
  - Builds the exact sentence required by the assignment brief, rounding
  the rate and inverse rate to 4 decimal places and the amounts to 2
  decimal places.

### `app.py` - the Streamlit interface

Builds the page and wires the two modules above together. It contains no
direct `requests` calls and no conversion maths itself:

- **`load_currencies()`** - Calls `get_currencies()`, wrapped in
  `@st.cache_data(ttl=3600)` so the currency list is fetched once and
  reused for an hour instead of being re-fetched on every button click.
- **`currency_label(code)`** - Formats a currency code with its name for
  display in the dropdowns, e.g. `"AUD - Australian Dollar"`.
- **`default_index(code, fallback=0)`** - Returns the position of a
  currency code in the sorted currency list (used to default the two
  dropdowns to AUD and USD), or `fallback` if the code isn't found.
- **`display_conversion(rate, rate_date)`** - Calls `convert_amount()` and
  `format_conversion_result()` and shows the resulting sentence with
  `st.text()`.
- **`display_rate_trend()`** - Calls `get_time_series()` for the selected
  currency pair over the last `TREND_PERIOD_DAYS` (~3 years) and plots it
  with `st.line_chart`. Does nothing if the currencies are the same or if
  the series comes back empty, and shows a warning (not an error) instead
  of crashing if the chart data can't be fetched, since the main
  conversion result has already been shown by this point.

The rest of `app.py` is the Streamlit layout itself: the title, the
number input, the two currency select boxes, the "Get Latest Rate" and
"Get Historical Rate" buttons, the date input, and the `try`/`except`
blocks around each API call that turn an `ApiError` into a red
`st.error()` message instead of a crash.

## Citation

### API

- Frankfurter. (n.d.). *Frankfurter Exchange Rates API* [API documentation].
  Retrieved September 2026, from https://www.frankfurter.app/docs/
  - Used for all currency, latest-rate, and historical-rate data in this
  project (`frankfurter.py`).

### Software libraries

- Streamlit Inc. (n.d.). *Streamlit documentation*.
  https://docs.streamlit.io/ - Used to build the web interface in `app.py`
  (`st.number_input`, `st.selectbox`, `st.date_input`, `st.button`,
  `st.cache_data`, `st.error`).
- Python Software Foundation. (n.d.). *requests: HTTP for Humans*
  documentation. https://docs.python-requests.org/ - Used in `api.py` to
  make HTTP GET requests to the Frankfurter API.
- Python Software Foundation. (n.d.). *datetime - Basic date and time
  types*. https://docs.python.org/3/library/datetime.html - Used in
  `frankfurter.py` and `app.py` to work with the historical date input.

### AI assistance

Generative AI (Anthropic's Claude) was used to assist with this
assignment, in accordance with the subject's generative AI policy. It was
used to help design the module structure, write and review the Python
code, draft this README, and generate test cases using mocked API
responses. All API endpoints, calculations, and the required output
format were taken directly from the assignment brief; the AI-generated
code was read, checked against the brief, and tested (with mocked data)
before submission.

*(If your subject requires a specific AI-use declaration format or
statement, replace this section with the exact wording from your subject
outline.)*

## Testing Performed

The calculation and error-handling logic (`api.py`, `frankfurter.py`,
`currency.py`) was tested offline using mocked API responses standing in
for real Frankfurter replies, covering:

- AUD → USD and USD → EUR conversions
- A valid historical date (matching the brief's own worked AUD → BGN
  example - the output matched exactly, including the 1.5565 inverse rate)
- An amount of `0`
- Same source and destination currency
- A simulated network failure
- A non-200 API response
- Missing rate data for a currency
- A future historical date
- Division-by-zero safety in the inverse rate calculation
- A 3-year time series for the rate trend chart, including the
  same-currency case (returns an empty series instead of erroring) and a
  malformed response (raises `ApiError` cleanly)

`streamlit run app.py` was also run locally and confirmed to start the
server and serve the page without errors. Live end-to-end calls to the
real Frankfurter API were not able to be executed in the development
environment used (outbound network access to the API was blocked there),
so the final currency dropdown population and live rate lookups should
still be spot-checked by running the app with a normal internet
connection before submission.

## Assumptions

- Rates and inverse rates are rounded to 4 decimal places and amounts to
  2 decimal places in the displayed message, for a consistent,
  currency-appropriate format (the brief's own examples round
  inconsistently).
- A same-currency conversion (e.g. AUD → AUD) returns a rate of `1.0`
  without calling the API, since Frankfurter excludes the base currency
  from its `rates` object.
