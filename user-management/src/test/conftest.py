import pytest
import os
import sys
from fastapi.testclient import TestClient

# Set environment variable for testing *before* importing the app
os.environ["TESTING"] = "true"

# Ensure the src directory is in the Python path
# Go up from test/ to src/
SRC_DIR_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if SRC_DIR_PATH not in sys.path:
    sys.path.insert(0, SRC_DIR_PATH)

# Now we can import the app and db functions relative to the src directory
from main.main import app
from main.models.user_model import initialize_database, clear_test_database, DB_PATH

@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Ensure TESTING env var is set for the whole session."""
    # The os.environ set above handles this, but this confirms it.
    assert os.environ["TESTING"] == "true"
    yield
    # Cleanup after session if needed, though function scope cleanup is usually preferred

@pytest.fixture(scope="function")
def test_db():
    """Fixture to ensure a clean database for each test function."""
    # Clear the table (if exists) and re-initialize schema
    clear_test_database()
    initialize_database()
    yield
    # Teardown: clear the database again after the test runs
    clear_test_database()
    # Optional: remove the test db file itself if desired
    # if os.path.exists(DB_PATH):
    #     os.remove(DB_PATH)

@pytest.fixture(scope="module")
def client() -> TestClient:
    """Provides a FastAPI TestClient instance for the module."""
    # This client will use the app instance which, due to os.environ["TESTING"],
    # will be configured to use the test database via the user_model import.
    with TestClient(app) as c:
        yield c 