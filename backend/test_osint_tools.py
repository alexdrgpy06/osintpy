import pytest
from agents.osint_tools import OSINTToolAgent

def test_sanitize_cli_arg():
    # Test strings with leading hyphens
    assert OSINTToolAgent.sanitize_cli_arg("--help") == "help"
    assert OSINTToolAgent.sanitize_cli_arg("-h") == "h"
    assert OSINTToolAgent.sanitize_cli_arg("---verbose") == "verbose"

    # Test strings without leading hyphens
    assert OSINTToolAgent.sanitize_cli_arg("john.doe") == "john.doe"
    assert OSINTToolAgent.sanitize_cli_arg("admin_123") == "admin_123"

    # Test strings with internal or trailing hyphens
    assert OSINTToolAgent.sanitize_cli_arg("john-doe") == "john-doe"
    assert OSINTToolAgent.sanitize_cli_arg("user-name-") == "user-name-"

    # Test edge cases
    assert OSINTToolAgent.sanitize_cli_arg("") == ""
    assert OSINTToolAgent.sanitize_cli_arg("-") == ""
    assert OSINTToolAgent.sanitize_cli_arg("--") == ""

    # Test non-string inputs (should convert to string or handle safely, though type hinting expects str)
    assert OSINTToolAgent.sanitize_cli_arg(123) == "123"
    assert OSINTToolAgent.sanitize_cli_arg(-123) == "123"
    assert OSINTToolAgent.sanitize_cli_arg(None) == ""
