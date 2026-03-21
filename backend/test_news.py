import pytest
from unittest.mock import patch
from news import NewsScraper

@pytest.mark.asyncio
async def test_search_ddg_news_exception():
    with patch('news.DDGS') as mock_ddgs:
        # Mock the __enter__ to raise an exception, or the news method
        mock_instance = mock_ddgs.return_value.__enter__.return_value
        mock_instance.news.side_effect = Exception("Mocked exception")

        results = await NewsScraper.search_ddg_news("test query")

        assert results == []
