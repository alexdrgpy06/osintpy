import pytest
from agents.osint_tools import OSINTToolAgent

def test_sanitize_cli_args_strips_leading_dashes():
    assert OSINTToolAgent.sanitize_cli_args("--help") == "help"
    assert OSINTToolAgent.sanitize_cli_args("-v") == "v"
    assert OSINTToolAgent.sanitize_cli_args("---admin") == "admin"
    assert OSINTToolAgent.sanitize_cli_args("-") == ""

def test_sanitize_cli_args_removes_invalid_characters():
    assert OSINTToolAgent.sanitize_cli_args("admin&") == "admin"
    assert OSINTToolAgent.sanitize_cli_args("user|name") == "username"
    assert OSINTToolAgent.sanitize_cli_args("user;id") == "userid"
    assert OSINTToolAgent.sanitize_cli_args("user`name") == "username"
    assert OSINTToolAgent.sanitize_cli_args("$(whoami)") == "whoami"
    assert OSINTToolAgent.sanitize_cli_args("test<>") == "test"

def test_sanitize_cli_args_keeps_valid_characters():
    assert OSINTToolAgent.sanitize_cli_args("user.name") == "user.name"
    assert OSINTToolAgent.sanitize_cli_args("user_name") == "user_name"
    assert OSINTToolAgent.sanitize_cli_args("user@domain") == "user@domain"
    assert OSINTToolAgent.sanitize_cli_args("user+name") == "user+name"
    assert OSINTToolAgent.sanitize_cli_args("user-name") == "user-name"

def test_sanitize_cli_args_complex_injection():
    assert OSINTToolAgent.sanitize_cli_args("--out=/tmp/file user") == "outtmpfileuser"
    assert OSINTToolAgent.sanitize_cli_args("-u admin; rm -rf /") == "uadminrm-rf"

def test_sanitize_cli_args_empty_input():
    assert OSINTToolAgent.sanitize_cli_args("") == ""
    assert OSINTToolAgent.sanitize_cli_args(None) == ""
