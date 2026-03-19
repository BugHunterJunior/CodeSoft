import sqlite3
import click
from flask import g
import config


def get_db():
    """Return a database connection, reusing one within the same request."""
    if "db" not in g:
        g.db = sqlite3.connect(
            config.DATABASE,
            detect_types=sqlite3.PARSE_DECLTYPES,
        )
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db(e=None):
    """Close the database connection at the end of the request."""
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    """Create all tables if they don't exist yet."""
    db = get_db()
    db.executescript(
        """
        CREATE TABLE IF NOT EXISTS users (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            username    TEXT    NOT NULL UNIQUE,
            email       TEXT    NOT NULL UNIQUE,
            password_hash TEXT  NOT NULL,
            created_at  TEXT    NOT NULL DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS tasks (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            title       TEXT    NOT NULL,
            description TEXT,
            priority    TEXT    NOT NULL DEFAULT 'medium',
            due_date    TEXT,
            is_complete INTEGER NOT NULL DEFAULT 0,
            created_at  TEXT    NOT NULL DEFAULT (datetime('now'))
        );
        """
    )
    db.commit()


def init_app(app):
    """Register database functions with the Flask app."""
    app.teardown_appcontext(close_db)

    @app.cli.command("init-db")
    def init_db_command():
        """CLI command: flask init-db"""
        init_db()
        click.echo("Database initialised.")
