import os
import pytest
from src.config import Settings

def test_config_fails_without_required_gcp_vars():
    # If MOCK_GCP is False and GCP_PROJECT_ID is empty
    with pytest.raises(ValueError):
        Settings(MOCK_GCP=False, GCP_PROJECT_ID="")

def test_config_succeeds_with_mock():
    # Should not raise
    settings = Settings(MOCK_GCP=True, GCP_PROJECT_ID="")
    assert settings.MOCK_GCP is True
