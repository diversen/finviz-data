# finviz-data

A simple package for getting fundamental data from finviz.com for a single ticker.

## Installation

```bash
uv add finviz-data
```

Alternatively, install it with pip:

```bash
pip install finviz-data
```

## Development

```bash
uv sync
uv run python -m unittest discover
```

By default, the live Finviz test is skipped. To run the full test suite without
skipping the live test, enable it with `FINVIZ_LIVE_TESTS=1`:

```bash
FINVIZ_LIVE_TESTS=1 uv run python -m unittest discover
```

The live test makes a real request to finviz.com and may still be skipped if
Finviz temporarily rate limits your IP.

## Usage

```python

from finviz_data import finviz_data

# Get the html soup for a single ticker
soup = finviz_data.get_soup('AAPL')

# Get the fundamentals for a single ticker
fundamentals = finviz_data.get_fundamentals(soup)

# Get the fundamentals where all is formatted to float values where possible
fundamentals = finviz_data.get_fundementals_float(soup)

# Get basic company info, sector, ticker etc. 
company_info = finviz_data.get_company_info(soup)
```
