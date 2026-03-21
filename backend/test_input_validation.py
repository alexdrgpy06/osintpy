import pytest
from agents.osint_tools import OSINTToolAgent

def test_is_safe_input():
    # Safe inputs
    assert OSINTToolAgent._is_safe_input("johndoe") == True
    assert OSINTToolAgent._is_safe_input("john.doe") == True
    assert OSINTToolAgent._is_safe_input("john-doe") == True
    assert OSINTToolAgent._is_safe_input("john_doe") == True
    assert OSINTToolAgent._is_safe_input("john123") == True
    assert OSINTToolAgent._is_safe_input("john@example.com") == True
    assert OSINTToolAgent._is_safe_input("john+alias@example.com") == True

    # Unsafe inputs
    assert OSINTToolAgent._is_safe_input("-johndoe") == False
    assert OSINTToolAgent._is_safe_input("--johndoe") == False
    assert OSINTToolAgent._is_safe_input("john doe") == False
    assert OSINTToolAgent._is_safe_input("john;ls") == False
    assert OSINTToolAgent._is_safe_input("john&whoami") == False
    assert OSINTToolAgent._is_safe_input("john|echo") == False
    assert OSINTToolAgent._is_safe_input("") == False

def test_cli_tools_reject_unsafe():
    logs = []
    def callback(msg):
        logs.append(msg)

    # Test Maigret with unsafe input
    OSINTToolAgent.run_maigret_live("-h", callback, [], [])
    assert len(logs) == 1
    assert "Invalid username format" in logs[0]

    # Test Sherlock with unsafe input
    logs.clear()
    OSINTToolAgent.run_sherlock_live("--version", callback, [], [])
    assert len(logs) == 1
    assert "Invalid username format" in logs[0]

    # Test Blackbird with unsafe input
    logs.clear()
    OSINTToolAgent.run_blackbird_live("user;ls", callback, [], [])
    assert len(logs) == 1
    assert "Invalid username format" in logs[0]

if __name__ == "__main__":
    pytest.main(["-v", "backend/test_input_validation.py"])
