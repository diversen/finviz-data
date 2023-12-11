# get html from url
import requests
from bs4 import BeautifulSoup


def get_soup(ticker) -> BeautifulSoup:
    url = "https://finviz.com/quote.ashx?t=" + ticker
    html = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}).text
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


def get_fundamentals_float(soup: BeautifulSoup):
    fundamentals = get_fundamentals(soup)
    return _convert_to_floats(fundamentals)


def get_company_info(soup: BeautifulSoup):
    # Finding the first inner div of the element with class 'quote-links'
    first_inner_div = soup.find("div", class_="quote-links").find("div")

    # Extracting all links from the first inner div
    links = first_inner_div.find_all("a")

    # Extracting text values of the links and assigning them to the appropriate keys in the 'base_info' dictionary
    base_info = {
        "sector": links[0].text,
        "industry": links[1].text,
        "country": links[2].text,
        "exchange": links[3].text,
    }

    return base_info


def _convert_to_floats(data_dict):
    """
    Converts values in a dictionary to floats where applicable.
    - Replaces single dash ('-') with None.
    - Splits values representing a range (e.g., '10.86 - 19.08') into two separate keys.
    - Converts values with '%' to proportionate floats.
    - Converts values ending in 'M', 'B', or 'T' to their numeric equivalents in millions, billions, or trillions.
    - Converts numeric strings with commas (e.g., '30,196,932') into floats.
    """

    def _convert_value(value):
        if value is None:
            return None
        if "%" in value:
            first_percentage = value.split()[0]
            return float(first_percentage.strip("%")) / 100
        elif value.endswith("M"):
            return float(value.strip("M")) * 1e6
        elif value.endswith("B"):
            return float(value.strip("B")) * 1e9
        elif value.endswith("T"):
            return float(value.strip("T")) * 1e12
        elif value.replace(".", "", 1).replace(",", "").isdigit():
            return float(value.replace(",", ""))
        else:
            return value

    week_range_52 = data_dict["52W Range"].split("-")
    data_dict["52 low"] = week_range_52[0]
    data_dict["52 high"] = week_range_52[1]

    # Remove 52W Range
    del data_dict["52W Range"]

    new_data = {}
    for key, value in data_dict.items():
        if value == "-":
            new_data[key] = None
        else:
            new_data[key] = _convert_value(value)

    return new_data
