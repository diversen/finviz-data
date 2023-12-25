# finviz-data

A simple package for getting fundamental data from finviz.com for a single ticker.

## Installation

```bash
pip install git+https://github.com/diversen/finviz-data
```

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
