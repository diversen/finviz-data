from finviz_data import finviz_data

# import python unit test
import os
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from bs4 import BeautifulSoup


ticker = "AAPL"
FIXTURE = Path(__file__).resolve().parents[1] / "finviz_example.html"


class TestFinvizData(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = FIXTURE.read_text(encoding="utf-8")
        cls.soup = BeautifulSoup(cls.html, "html.parser")

    def test_get_soup(self):
        response = Mock(text=self.html)
        with patch("finviz_data.finviz_data.requests.get", return_value=response) as get:
            soup = finviz_data.get_soup(ticker)

        get.assert_called_once_with(
            "https://finviz.com/stock?t=AAPL&p=d",
            impersonate="chrome",
        )
        self.assertIsNotNone(soup)
        self.assertEqual(soup.find("h1").get_text(strip=True), ticker)

    @unittest.skipUnless(
        os.getenv("FINVIZ_LIVE_TESTS") == "1",
        "set FINVIZ_LIVE_TESTS=1 to run live Finviz tests",
    )
    def test_get_soup_live(self):
        soup = finviz_data.get_soup(ticker)
        page_text = soup.get_text(" ", strip=True)

        if "temporarily rate limited" in page_text:
            self.skipTest("Finviz temporarily rate limited this IP")

        self.assertIsNotNone(soup)
        table = soup.find("table", class_="snapshot-table2")
        self.assertIsNotNone(table, page_text[:500])

        header = soup.find("h1", class_="quote-header_ticker-wrapper_ticker")
        self.assertIsNotNone(header, page_text[:500])
        self.assertEqual(header.get_text(strip=True), ticker)

        fundamentals = finviz_data.get_fundamentals(soup)
        self.assertIn("Market Cap", fundamentals)
        self.assertIn("P/E", fundamentals)

        company_info = finviz_data.get_company_info(soup)
        self.assertEqual(company_info["Ticker"], ticker)
        self.assertIn("Company", company_info)

    def test_get_fundamentals(self):
        fundamentals = finviz_data.get_fundamentals(self.soup)
        self.assertIsInstance(fundamentals, dict)
        self.assertEqual(fundamentals["Market Cap"], "4282.54B")
        self.assertEqual(fundamentals["P/E"], "35.27")
        self.assertEqual(fundamentals["Volatility"], "3.27% 2.16%")

    def test_get_company_info(self):
        company_info = finviz_data.get_company_info(self.soup)
        self.assertIsInstance(company_info, dict)

        # check if company_info has all the keys
        self.assertEqual(company_info["Ticker"], ticker)
        self.assertEqual(company_info["Company"], "Apple Inc")
        self.assertEqual(company_info["Sector"], "Technology")
        self.assertEqual(company_info["Industry"], "Consumer Electronics")
        self.assertEqual(company_info["Country"], "USA")
        self.assertEqual(company_info["Exchange"], "NASD")
        self.assertIn("Company", company_info)
        self.assertIn("Sector", company_info)
        self.assertIn("Industry", company_info)
        self.assertIn("Country", company_info)
        self.assertIn("Exchange", company_info)

    def test_get_get_fundamentals_converted(self):
        fundamentals_converted = finviz_data.get_fundamentals_float(self.soup)
        self.assertIsInstance(fundamentals_converted, dict)
        self.assertEqual(fundamentals_converted["Market Cap"], 4282.54e9)
        self.assertEqual(fundamentals_converted["P/E"], 35.27)
        self.assertEqual(fundamentals_converted["Volatility Week"], 0.0327)
        self.assertEqual(fundamentals_converted["Volatility Month"], 0.0216)

    def test_convert_percentage(self):
        value = "1.39%"
        converted_value = finviz_data._convert_value(value)
        self.assertEqual(converted_value, 0.0139)

    def test_convert_million(self):
        value = "1.39M"
        converted_value = finviz_data._convert_value(value)
        self.assertEqual(converted_value, 1390000)


if __name__ == "__main__":
    unittest.main()
