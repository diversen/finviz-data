from finviz_data import finviz_data


ticker = "AAPL"

soup = finviz_data.get_soup(ticker)
fundamentals = finviz_data.get_fundamentals(soup)
print(f"fundamentals\n{fundamentals}\n")

company_info = finviz_data.get_company_info(soup)
print(f"company_info\n{company_info}\n")

fundamentals_converted = finviz_data.get_fundamentals_float(soup)
print(f"fundamentals_converted\n{fundamentals_converted}\n")
