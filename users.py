
import json
from pathlib import Path

from auth import hash_password, verify_password

# Local user database for development
USERS_FILE = Path("data/users.json")

VALID_ROLES = {"admin", "employee"}


def load_users():
    """Load user accounts from the JSON file."""
    if not USERS_FILE.exists():
        return {}

    with USERS_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def save_users(users):
    """Save user accounts."""
    USERS_FILE.parent.mkdir(parents=True, exist_ok=True)

    with USERS_FILE.open("w", encoding="utf-8") as file:
        json.dump(users, file, indent=4)


def create_user(username, password, role="employee"):
    """Create a user with a hashed password."""
    if not username or not username.strip():
        raise ValueError("Username cannot be empty")

    if not password or len(password) < 12:
        raise ValueError("Password must contain at least 12 characters")

    if role not in VALID_ROLES:
        raise ValueError("Invalid user role")

    users = load_users()

    if username in users:
        raise ValueError("Username already exists")

    users[username] = {
        "password_hash": hash_password(password),
        "role": role,
    }

    save_users(users)

    return {
        "username": username,
        "role": role,
    }


def authenticate_user(username, password):
    """Verify login credentials."""
    users = load_users()

    user = users.get(username)

    if not user:
        return None

    if not verify_password(
        password,
        user["password_hash"]
    ):
        return None

    return {
        "username": username,
        "role": user["role"],
    }
