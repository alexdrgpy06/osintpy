import pytest
from agents.osint_tools import OSINTToolAgent

def test_extract_platform_name_happy_path():
    assert OSINTToolAgent.extract_platform_name("https://github.com/user") == "GitHub"
    assert OSINTToolAgent.extract_platform_name("https://www.twitter.com/user") == "X/Twitter"
    assert OSINTToolAgent.extract_platform_name("http://instagram.com/user") == "Instagram"

def test_extract_platform_name_parent_domain():
    # 'profile.example.com' shouldn't work if 'example.com' isn't in PLATFORM_MAP, but 'open.spotify.com' should
    # Wait, 'open.spotify.com' is actually IN the PLATFORM_MAP. Let's see if something else works.
    # What if we pass 'music.github.com'? 'github.com' is in PLATFORM_MAP
    assert OSINTToolAgent.extract_platform_name("https://music.github.com/user") == "GitHub"

def test_extract_platform_name_fallback():
    assert OSINTToolAgent.extract_platform_name("https://example.com") == "Example"
    assert OSINTToolAgent.extract_platform_name("https://sub.unmapped.net") == "Sub"

def test_extract_platform_name_error_path():
    # Passing None should raise an exception in urlparse, which will be caught
    # and "Unknown" will be returned
    assert OSINTToolAgent.extract_platform_name(None) == "Unknown"

    # Passing a non-string object that raises an exception in urlparse (e.g. integer)
    assert OSINTToolAgent.extract_platform_name(12345) == "Unknown"

    # Passing a dict
    assert OSINTToolAgent.extract_platform_name({"url": "https://github.com/user"}) == "Unknown"
