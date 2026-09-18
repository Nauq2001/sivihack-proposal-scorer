from __future__ import annotations

import pytest


@pytest.fixture
def rfp_text() -> str:
    return """# Warehouse Inventory Dashboard
Client: NordFrame Logistics GmbH

## Requirements
Integration with our existing PostgreSQL database — no migration to a new database.
Support terms after go-live.
"""


@pytest.fixture
def base_criteria():
    from rfp_analyst.config import base_criteria

    return base_criteria()

