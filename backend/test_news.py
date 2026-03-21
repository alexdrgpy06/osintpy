import pytest
import asyncio
from unittest.mock import patch, MagicMock
from news import NewsScraper

@pytest.mark.asyncio
async def test_search_ddg_news_success():
    mock_results = [
        {
            "title": "Test News 1",
            "url": "https://example.com/1",
            "source": "ABC Color",
            "date": "2023-10-01T10:00:00Z",
            "body": "This is a test news snippet 1."
        },
        {
            "title": "Test News 2",
            "url": "https://example.com/2",
            "source": "Ultima Hora",
            "date": "2023-10-01T11:00:00Z",
            "body": "This is a test news snippet 2."
        }
    ]

    with patch("news.DDGS") as MockDDGS:
        # Configure the mock to work as a context manager
        mock_ddgs_instance = MagicMock()
        MockDDGS.return_value.__enter__.return_value = mock_ddgs_instance
        mock_ddgs_instance.news.return_value = mock_results

        results = await NewsScraper.search_ddg_news("corrupción", max_results=2)

        # Verify the mock was called correctly
        mock_ddgs_instance.news.assert_called_once_with(
            "corrupción", region='es-py', safesearch='off', timelimit='m', max_results=2
        )

        # Verify the results are mapped correctly
        assert len(results) == 2
        assert results[0] == {
            "title": "Test News 1",
            "url": "https://example.com/1",
            "source": "ABC Color",
            "date": "2023-10-01T10:00:00Z",
            "snippet": "This is a test news snippet 1."
        }
        assert results[1] == {
            "title": "Test News 2",
            "url": "https://example.com/2",
            "source": "Ultima Hora",
            "date": "2023-10-01T11:00:00Z",
            "snippet": "This is a test news snippet 2."
        }

@pytest.mark.asyncio
async def test_search_ddg_news_exception():
    with patch("news.DDGS") as MockDDGS:
        mock_ddgs_instance = MagicMock()
        MockDDGS.return_value.__enter__.return_value = mock_ddgs_instance
        # Make the news method raise an exception
        mock_ddgs_instance.news.side_effect = Exception("API connection error")

        # Test if it handles the exception and returns an empty list
        results = await NewsScraper.search_ddg_news("corrupción")

        assert results == []
