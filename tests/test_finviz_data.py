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
        self.assertAlmostEqual(fundamentals_converted["Volatility Week"], 0.0327)
        self.assertAlmostEqual(fundamentals_converted["Volatility Month"], 0.0216)
        self.assertEqual(fundamentals_converted["52W High Price"], 317.4)
        self.assertAlmostEqual(fundamentals_converted["52W High Change"], -0.0813)
        self.assertEqual(fundamentals_converted["52W Low Price"], 195.07)
        self.assertAlmostEqual(fundamentals_converted["52W Low Change"], 0.4947)
        self.assertAlmostEqual(fundamentals_converted["EPS past 3Y"], 0.0689)
        self.assertAlmostEqual(fundamentals_converted["EPS past 5Y"], 0.1791)
        self.assertAlmostEqual(fundamentals_converted["Sales past 3Y"], 0.0181)
        self.assertAlmostEqual(fundamentals_converted["Sales past 5Y"], 0.0871)
        self.assertAlmostEqual(fundamentals_converted["Dividend Gr. 3Y"], 0.0426)
        self.assertAlmostEqual(fundamentals_converted["Dividend Gr. 5Y"], 0.0498)
        self.assertEqual(fundamentals_converted["Dividend Est. Amount"], 1.08)
        self.assertAlmostEqual(fundamentals_converted["Dividend Est. Yield"], 0.0037)
        self.assertEqual(fundamentals_converted["Dividend TTM Amount"], 1.05)
        self.assertAlmostEqual(fundamentals_converted["Dividend TTM Yield"], 0.0036)
        self.assertEqual(fundamentals_converted["Optionable"], True)
        self.assertEqual(fundamentals_converted["Shortable"], True)
        self.assertAlmostEqual(fundamentals_converted["EPS Surprise"], 0.033)
        self.assertAlmostEqual(fundamentals_converted["Sales Surprise"], 0.0158)
        self.assertEqual(fundamentals_converted["Earnings Date"], "Apr 30")
        self.assertEqual(fundamentals_converted["Earnings Time"], "AMC")
        self.assertEqual(fundamentals_converted["IPO"], "1980-12-12")
        self.assertEqual(fundamentals_converted["Dividend Ex-Date"], "2026-05-11")
        self.assertIsNone(fundamentals_converted["Trades"])

        self.assertNotIn("Volatility", fundamentals_converted)
        self.assertNotIn("52W High", fundamentals_converted)
        self.assertNotIn("52W Low", fundamentals_converted)
        self.assertNotIn("EPS past 3/5Y", fundamentals_converted)
        self.assertNotIn("Sales past 3/5Y", fundamentals_converted)
        self.assertNotIn("Dividend Gr. 3/5Y", fundamentals_converted)
        self.assertNotIn("Dividend Est.", fundamentals_converted)
        self.assertNotIn("Dividend TTM", fundamentals_converted)
        self.assertNotIn("Option/Short", fundamentals_converted)
        self.assertNotIn("EPS/Sales Surpr.", fundamentals_converted)
        self.assertNotIn("Earnings", fundamentals_converted)

    def test_convert_percentage(self):
        value = "1.39%"
        converted_value = finviz_data._convert_value(value)
        self.assertEqual(converted_value, 0.0139)

    def test_convert_million(self):
        value = "1.39M"
        converted_value = finviz_data._convert_value(value)
        self.assertEqual(converted_value, 1390000)

    def test_convert_negative_number(self):
        value = "-1.39"
        converted_value = finviz_data._convert_value(value)
        self.assertEqual(converted_value, -1.39)

    def test_convert_empty_value(self):
        self.assertIsNone(finviz_data._convert_value(""))
        self.assertIsNone(finviz_data._convert_value("-"))


if __name__ == "__main__":
    unittest.main()
