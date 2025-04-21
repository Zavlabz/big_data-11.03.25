import pytest
import requests
from cat import CatFactProcessor, APIError

class MockResponseSuccess:
    def __init__(self, fact):
        self._fact = fact
    def raise_for_status(self):
        pass
    def json(self):
        return {"fact": self._fact}

class MockResponseHTTPError:
    def raise_for_status(self):
        raise requests.exceptions.HTTPError("500 Server Error")

class MockResponseInvalidJSON:
    def raise_for_status(self):
        pass
    def json(self):
        raise ValueError("Invalid JSON")


def test_get_fact_success(monkeypatch):
    processor = CatFactProcessor()
    monkeypatch.setattr(requests, 'get', lambda url: MockResponseSuccess("Cats are great!"))
    fact = processor.get_fact()
    assert fact == "Cats are great!"
    assert processor.last_fact == "Cats are great!"


def test_get_fact_http_error(monkeypatch):
    processor = CatFactProcessor()
    monkeypatch.setattr(requests, 'get', lambda url: MockResponseHTTPError())
    with pytest.raises(APIError) as excinfo:
        processor.get_fact()
    assert "Ошибка при запросе к API" in str(excinfo.value)


def test_get_fact_connection_error(monkeypatch):
    processor = CatFactProcessor()
    monkeypatch.setattr(requests, 'get', lambda url: (_ for _ in ()).throw(requests.exceptions.ConnectionError("Connection failed")))
    with pytest.raises(APIError) as excinfo:
        processor.get_fact()
    assert "Ошибка при запросе к API" in str(excinfo.value)


def test_get_fact_json_error(monkeypatch):
    processor = CatFactProcessor()
    monkeypatch.setattr(requests, 'get', lambda url: MockResponseInvalidJSON())
    # JSONDecode error is not caught, so original ValueError propagates
    with pytest.raises(ValueError):
        processor.get_fact()


def test_get_fact_analysis_empty():
    processor = CatFactProcessor()
    result = processor.get_fact_analysis()
    assert result == {"length": 0, "letter_frequencies": {}}


def test_get_fact_analysis_with_content():
    processor = CatFactProcessor()
    processor.last_fact = "AaBb! "
    result = processor.get_fact_analysis()
    expected_length = len(processor.last_fact)
    assert result["length"] == expected_length
    # вручную считаем частоты
    expected_freq = {}
    for ch in processor.last_fact.lower():
        expected_freq[ch] = expected_freq.get(ch, 0) + 1
    assert result["letter_frequencies"] == expected_freq


def test_integration_flow(monkeypatch):
    processor = CatFactProcessor()
    monkeypatch.setattr(requests, 'get', lambda url: MockResponseSuccess("Cats rule"))
    fact = processor.get_fact()
    assert fact == "Cats rule"
    analysis = processor.get_fact_analysis()
    assert analysis["length"] == len("Cats rule")
    # проверяем частоты каждого символа
    expected_freq = {}
    for ch in "cats rule":  # lowercased
        expected_freq[ch] = expected_freq.get(ch, 0) + 1
    assert analysis["letter_frequencies"] == expected_freq
