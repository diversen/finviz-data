from finviz_data import finviz_data

# import python unit test
import unittest


ticker = "IPI"


class TestFinvizData(unittest.TestCase):
    def test_get_soup(self):
        soup = finviz_data.get_soup(ticker)
        self.assertIsNotNone(soup)

    def test_get_fundamentals(self):
        soup = finviz_data.get_soup(ticker)
        fundamentals = finviz_data.get_fundamentals(soup)
        self.assertIsInstance(fundamentals, dict)

    def test_get_company_info(self):
        soup = finviz_data.get_soup(ticker)
        company_info = finviz_data.get_company_info(soup)
        self.assertIsInstance(company_info, dict)

        # check if company_info has all the keys
        self.assertIn("sector", company_info)
        self.assertIn("industry", company_info)
        self.assertIn("country", company_info)
        self.assertIn("exchange", company_info)

    def test_get_get_fundamentals_converted(self):
        soup = finviz_data.get_soup(ticker)
        fundamentals_converted = finviz_data.get_fundamentals_float(soup)
        self.assertIsInstance(fundamentals_converted, dict)

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
