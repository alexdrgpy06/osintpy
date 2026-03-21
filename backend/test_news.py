import pytest
from unittest.mock import patch, MagicMock
from news import NewsScraper

@pytest.mark.asyncio
async def test_search_ddg_news_success():
    mock_results = [
        {
            "title": "Noticia 1",
            "url": "http://test.com/1",
            "source": "Fuente 1",
            "date": "2023-01-01",
            "body": "Snippet 1"
        },
        {
            "title": "Noticia 2",
            "url": "http://test.com/2",
            "source": "Fuente 2",
            "date": "2023-01-02",
            "body": "Snippet 2"
        }
    ]

    with patch('news.DDGS') as MockDDGS:
        mock_instance = MagicMock()
        MockDDGS.return_value.__enter__.return_value = mock_instance
        mock_instance.news.return_value = mock_results

        results = await NewsScraper.search_ddg_news("paraguay", max_results=2)

        mock_instance.news.assert_called_once_with(
            "paraguay", region='es-py', safesearch='off', timelimit='m', max_results=2
        )

        assert len(results) == 2
        assert results[0]["title"] == "Noticia 1"
        assert results[0]["url"] == "http://test.com/1"
        assert results[0]["source"] == "Fuente 1"
        assert results[0]["date"] == "2023-01-01"
        assert results[0]["snippet"] == "Snippet 1"

        assert results[1]["title"] == "Noticia 2"
        assert results[1]["url"] == "http://test.com/2"
        assert results[1]["source"] == "Fuente 2"
        assert results[1]["date"] == "2023-01-02"
        assert results[1]["snippet"] == "Snippet 2"


@pytest.mark.asyncio
async def test_search_ddg_news_exception():
    with patch('news.DDGS') as MockDDGS:
        mock_instance = MagicMock()
        MockDDGS.return_value.__enter__.return_value = mock_instance
        mock_instance.news.side_effect = Exception("API Error")

        results = await NewsScraper.search_ddg_news("error query")

        assert results == []
