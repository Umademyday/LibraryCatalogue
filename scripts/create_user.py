#!/usr/bin/env python3
"""
CLI tool to create users for the Library Catalogue.

Usage:
    python -m scripts.create_user --username admin --email admin@lib.local --admin
    python -m scripts.create_user -u reader -e reader@lib.local
"""
import argparse
import getpass
import sys

from passlib.hash import bcrypt

from app.database.session import SessionLocal
from app.models import User


def create_user(username: str, email: str, password: str, is_admin: bool = False) -> User:
    """Create a new user in the database."""
    session = SessionLocal()
    try:
        # Check if user already exists
        existing = session.query(User).filter(
            (User.username == username) | (User.email == email)
        ).first()
        if existing:
            raise ValueError(f"User with username '{username}' or email '{email}' already exists")

        user = User(
            username=username,
            email=email,
            hashed_password=bcrypt.hash(password),
            is_admin=is_admin,
            is_active=True,
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        return user
    finally:
        session.close()


def main():
    parser = argparse.ArgumentParser(description="Create a new user for Library Catalogue")
    parser.add_argument("-u", "--username", required=True, help="Username for the new user")
    parser.add_argument("-e", "--email", required=True, help="Email for the new user")
    parser.add_argument("--admin", action="store_true", help="Make user an admin")
    parser.add_argument("-p", "--password", help="Password (will prompt if not provided)")

    args = parser.parse_args()

    password = args.password
    if not password:
        password = getpass.getpass("Enter password: ")
        confirm = getpass.getpass("Confirm password: ")
        if password != confirm:
            print("Error: Passwords do not match", file=sys.stderr)
            sys.exit(1)

    if len(password) < 8:
        print("Error: Password must be at least 8 characters", file=sys.stderr)
        sys.exit(1)

    try:
        user = create_user(args.username, args.email, password, args.admin)
        print(f"Created user: {user.username} (admin={user.is_admin})")
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error creating user: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
