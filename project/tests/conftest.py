import string
import random

import pytest
from starlette.testclient import TestClient

from app.main import create_application



@pytest.fixture
def generate_test_name() -> str:
    """Generates random valid name of length 18 characters with testing_ at the front."""
    return lambda: "testing_" + "".join(
        random.choice(string.ascii_lowercase) for _ in range(10)
    )


@pytest.fixture(scope="module")
def test_app():
    # set up
    app = create_application()
    with TestClient(app) as test_app:

        yield test_app


@pytest.fixture(scope="session", autouse=True)
def clean_upp_db():
    """Not implemented."""
    pass
