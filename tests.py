import unittest
from unittest.mock import patch, MagicMock
from file_for_test import CatFactProcessor, APIError
import requests


class CatFactProcessorTest(unittest.TestCase):
    def setUp(self):
        """Создает новый экземпляр перед каждым тестом"""
        self.processor = CatFactProcessor()

    @patch("requests.get")
    def test_fetch_fact_success(self, mock_get):
        """Проверяет успешное получение и сохранение факта о кошках"""
        example_fact = "Cats sleep for 70% of their lives."
        
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = {"fact": example_fact}
        mock_get.return_value = mock_response

        retrieved_fact = self.processor.get_fact()

        self.assertEqual(retrieved_fact, example_fact)
        self.assertEqual(self.processor.last_fact, example_fact)
        mock_get.assert_called_once_with("https://catfact.ninja/fact", timeout=5)

    @patch("requests.get")
    def test_fetch_fact_handles_request_failure(self, mock_get):
        """Проверяет, что при сбое запроса вызывается APIError"""
        mock_get.side_effect = requests.exceptions.Timeout("Request timeout")

        with self.assertRaises(APIError) as error:
            self.processor.get_fact()

        self.assertIn("Ошибка при запросе к API", str(error.exception))

    def test_fact_analysis_defaults_when_no_fact(self):
        """Проверяет, что анализ возвращает нулевые значения, если факт не задан"""
        result = self.processor.get_fact_analysis()
        self.assertEqual(result, {"length": 0, "letter_frequencies": {}})

    def test_fact_analysis_correct_values(self):
        """Проверяет корректность расчета длины и частоты букв"""
        self.processor.last_fact = "Cats purr loudly!"
        
        analysis = self.processor.get_fact_analysis()
        expected_frequencies = {"c": 1, "a": 1, "t": 1, "s": 1, "p": 1, "u": 2, "r": 2, "l": 2, "o": 1, "d": 1, "y": 1}
        
        self.assertEqual(analysis["length"], 17)
        self.assertEqual(analysis["letter_frequencies"], expected_frequencies)

    def test_fact_analysis_is_case_insensitive_and_ignores_non_letters(self):
        """Проверяет, что регистр игнорируется, а символы вне алфавита исключаются"""
        self.processor.last_fact = "Meow! 456 MEOw?"
        
        analysis = self.processor.get_fact_analysis()
        expected_frequencies = {"m": 2, "e": 2, "o": 2, "w": 2}
        
        self.assertEqual(analysis["length"], len("Meow! 456 MEOw?"))
        self.assertEqual(analysis["letter_frequencies"], expected_frequencies)

    def test_fetch_fact_preserves_state_on_failure(self):
        """Проверяет, что при ошибке last_fact остается неизменным"""
        self.processor.last_fact = "Cats have whiskers."
        
        with patch("requests.get", side_effect=requests.exceptions.RequestException):
            with self.assertRaises(APIError):
                self.processor.get_fact()

        self.assertEqual(self.processor.last_fact, "Cats have whiskers.")


if __name__ == "__main__":
    unittest.main()
