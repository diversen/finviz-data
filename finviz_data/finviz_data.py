from datetime import datetime

from bs4 import BeautifulSoup
from curl_cffi import requests


class FinvizRequestError(Exception):
    """Raised when Finviz returns an unsuccessful HTTP response."""


def get_soup(ticker) -> BeautifulSoup:
    url = f"https://finviz.com/stock?t={ticker}&p=d"
    response = requests.get(url, impersonate="chrome")
    status_code = getattr(response, "status_code", None)
    if isinstance(status_code, int) and status_code >= 400:
        raise FinvizRequestError(
            f"Finviz request failed for ticker {ticker!r}: "
            f"HTTP {status_code} ({url})"
        )

    html = response.text
    soup = BeautifulSoup(html, "html.parser")
    return soup


def get_fundamentals(soup: BeautifulSoup) -> dict:
    # get table with class='snapshot-table2'
    table = soup.find("table", {"class": "snapshot-table2"})

    # Initialize a dictionary to store the key-value pairs
    financial_data = {}

    # Iterate through all rows of the table
    for row in table.find_all("tr"):
        # Each cell in the row
        cells = row.find_all("td")
        for i in range(0, len(cells), 2):  # Step by 2 as key and value are in pairs
            key = cells[i].get_text().strip()
            value = cells[i + 1].get_text().strip()
            financial_data[key] = value

    return financial_data


def get_fundamentals_float(soup: BeautifulSoup) -> dict:
    fundamentals = get_fundamentals(soup)
    fundamentals_float = _convert_to_floats(fundamentals)

    return fundamentals_float


def get_company_info(soup: BeautifulSoup) -> dict:
    base_info = {}

    # Get ticker. Text ontent of quote-header_ticker-wrapper_ticker
    ticker = soup.find("h1", class_="quote-header_ticker-wrapper_ticker").text
    base_info["Ticker"] = ticker

    # Get company name. Text content of h2.quote-header_ticker-wrapper_company a
    company_name = (
        soup.find("h2", class_="quote-header_ticker-wrapper_company").text
    )
    base_info["Company"] = company_name.strip()

    # Finding the first inner div of the element with class 'quote-links'
    first_inner_div = soup.find("div", class_="quote-links").find("div")

    # Extracting all links from the first inner div
    links = first_inner_div.find_all("a")

    for link in links:
        href = link.get("href", "")
        if "f=sec_" in href:
            base_info["Sector"] = link.text
        elif "f=ind_" in href:
            base_info["Industry"] = link.text
        elif "f=geo_" in href:
            base_info["Country"] = link.text
        elif "f=exch_" in href:
            base_info["Exchange"] = link.text

    return base_info


def _is_float_like(val: str) -> bool:
    try:
        float(val)
        return True
    except ValueError:
        return False


def _convert_value(value: str):
    if value is None:
        return None

    value = value.strip()

    if value in ("", "-"):
        return None
    elif value.endswith("%") and _is_float_like(value.strip("%")):
        return float(value.strip("%")) / 100
    elif value.endswith("M") and _is_float_like(value.strip("M")):
        return float(value.strip("M")) * 1e6
    elif value.endswith("B") and _is_float_like(value.strip("B")):
        return float(value.strip("B")) * 1e9
    elif value.endswith("T") and _is_float_like(value.strip("T")):
        return float(value.strip("T")) * 1e12
    elif _is_float_like(value.replace(",", "")):
        return float(value.replace(",", ""))
    else:
        return value


def _convert_date(value: str):
    try:
        return datetime.strptime(value, "%b %d, %Y").date().isoformat()
    except ValueError:
        return _convert_value(value)


def _split_two_values(value: str, first_key: str, second_key: str) -> dict:
    values = value.split()
    if len(values) != 2:
        return {first_key: _convert_value(value), second_key: None}

    return {
        first_key: _convert_value(values[0]),
        second_key: _convert_value(values[1]),
    }


def _split_dividend(value: str, amount_key: str, yield_key: str) -> dict:
    values = value.replace("(", "").replace(")", "").split()
    if len(values) != 2:
        return {amount_key: _convert_value(value), yield_key: None}

    return {
        amount_key: _convert_value(values[0]),
        yield_key: _convert_value(values[1]),
    }


def _split_option_short(value: str) -> dict:
    values = [item.strip() for item in value.split("/")]
    if len(values) != 2:
        return {"Optionable": _convert_value(value), "Shortable": None}

    return {
        "Optionable": values[0] == "Yes",
        "Shortable": values[1] == "Yes",
    }


def _split_earnings(value: str) -> dict:
    values = value.split()
    if len(values) < 3:
        return {"Earnings Date": _convert_value(value), "Earnings Time": None}

    return {
        "Earnings Date": " ".join(values[:-1]),
        "Earnings Time": values[-1],
    }


def _convert_to_floats(data_dict: dict) -> dict:
    """
    Converts values in a dictionary to floats where applicable.
    - Replaces single dash ('-') with None.
    - Splits values representing a range (e.g., '10.86 - 19.08') into two separate keys.
    - Converts values with '%' to proportionate floats.
    - Converts values ending in 'M', 'B', or 'T' to their numeric equivalents in millions, billions, or trillions.
    - Converts numeric strings with commas (e.g., '30,196,932') into floats.
    """

    compound_fields = {
        "Volatility": lambda value: _split_two_values(
            value, "Volatility Week", "Volatility Month"
        ),
        "52W High": lambda value: _split_two_values(
            value, "52W High Price", "52W High Change"
        ),
        "52W Low": lambda value: _split_two_values(
            value, "52W Low Price", "52W Low Change"
        ),
        "EPS past 3/5Y": lambda value: _split_two_values(
            value, "EPS past 3Y", "EPS past 5Y"
        ),
        "Sales past 3/5Y": lambda value: _split_two_values(
            value, "Sales past 3Y", "Sales past 5Y"
        ),
        "Dividend Gr. 3/5Y": lambda value: _split_two_values(
            value, "Dividend Gr. 3Y", "Dividend Gr. 5Y"
        ),
        "EPS/Sales Surpr.": lambda value: _split_two_values(
            value, "EPS Surprise", "Sales Surprise"
        ),
        "Dividend Est.": lambda value: _split_dividend(
            value, "Dividend Est. Amount", "Dividend Est. Yield"
        ),
        "Dividend TTM": lambda value: _split_dividend(
            value, "Dividend TTM Amount", "Dividend TTM Yield"
        ),
        "Option/Short": _split_option_short,
        "Earnings": _split_earnings,
    }

    date_fields = {"IPO", "Dividend Ex-Date"}

    new_data = {}
    for key, value in data_dict.items():
        value = value.strip() if isinstance(value, str) else value

        if key in compound_fields:
            new_data.update(compound_fields[key](value))
        elif key in date_fields:
            new_data[key] = _convert_date(value)
        else:
            new_data[key] = _convert_value(value)

    return new_data
