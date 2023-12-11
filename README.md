# finviz-data

## Installation

```bash
pip install finviz-data
```

## Usage

```python

from finviz_data import finviz_data

# Get the data for a single ticker
soup = finviz_data.get_soup('AAPL')

# Get the fundamentals for a single ticker
fundamentals = finviz_data.get_fundamentals(soup)

# Get the fundamentals where all is formatted to float values where possible
fundamentals = finviz_data.get_fundementals_float(soup)

# Get basic company info
company_info = finviz_data.get_company_info(soup)



