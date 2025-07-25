# Example test for UAI core abstractions
import pytest

def test_import_uai():
    import unified_agent_interface as uai
    assert hasattr(uai, "__file__")
