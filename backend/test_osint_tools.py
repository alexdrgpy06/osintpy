import pytest
from agents.osint_tools import OSINTToolAgent

@pytest.mark.parametrize(
    "url, expected",
    [
        # Exact matches in PLATFORM_MAP
        ("https://github.com/someuser", "GitHub"),
        ("http://twitter.com/user", "X/Twitter"),
        ("https://x.com/user", "X/Twitter"),

        # With www. prefix
        ("https://www.linkedin.com/in/user", "LinkedIn"),
        ("http://www.instagram.com/user", "Instagram"),

        # Subdomains that resolve to parent domain in PLATFORM_MAP
        ("https://profile.github.com/user", "GitHub"),
        ("https://blog.stackoverflow.com/article", "StackOverflow"),

        # Unmapped domains fallback to capitalized first part
        ("https://example.com/user", "Example"),
        ("https://sub.mywebsite.org/page", "Sub"),

        # Edge cases and invalid inputs
        ("not_a_url", "Unknown"),
        ("", "Unknown"),
        (None, "Unknown"),
    ]
)
def test_extract_platform_name(url, expected):
    assert OSINTToolAgent.extract_platform_name(url) == expected
