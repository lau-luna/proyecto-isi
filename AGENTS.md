# AGENTS.md

Guidance for AI coding agents working in this repository.

## Project

Q&A website built with Flask (UNRC 2026, Software Engineering course).
Package lives in `src/proyecto/` (src layout, built with `uv_build`). Python `>=3.14`.

## Stack

- Flask + Jinja2 templates, Bulma CSS (CDN) for styling
- Flask-SQLAlchemy 3 with SQLAlchemy 2.0 typed models (`Mapped` / `mapped_column`)
- Flask-Migrate (Alembic) for schema changes
- argon2-cffi (`PasswordHasher`, argon2id) for password hashing
- pytest for tests, Ruff for lint/format
- `uv` for dependency and environment management

## Commands

```bash
uv sync                                         # install deps
uv run pytest                                   # run tests
uv run ruff check . && uv run ruff format .     # lint + format
uv run flask --app proyecto run --debug         # dev server
uv run flask --app proyecto db upgrade          # apply migrations
uv run flask --app proyecto db migrate -m "msg" # generate migration
```

## Layout

```
src/proyecto/
  __init__.py      # create_app(environment) app factory, registers blueprints
  config.py        # Development / Testing / Production configs, `config` dict
  extensions.py    # db (SQLAlchemy with DeclarativeBase), migrate
  models/          # one model per file (User.py, Category.py), imported in __init__.py
  routes/          # Flask blueprints (user.py -> /user/...)
  templates/       # Jinja2 templates, grouped by blueprint (user/register.html)
migrations/        # Alembic migrations (versions/ is committed)
tests/             # pytest; fixtures in conftest.py
docs/              # project docs (Spanish), class diagrams, pattern justification
```

## Conventions

- **App factory**: always build the app via `create_app("development" | "testing" | "production")`. Never create a module-level `Flask` instance.
- **Blueprints**: one blueprint per feature in `src/proyecto/routes/`, registered in `create_app`. Endpoint names are `"<bp>.<view>"` (e.g. `user.register`).
- **Models**:
  - Subclass `db.Model`, set `__tablename__`, use typed `Mapped[...]` columns.
  - Python type must match nullability (`Mapped[str | None]` ⇔ `nullable=True`).
  - Every new model MUST be imported in `src/proyecto/models/__init__.py`, or Alembic will not detect it.
- **Migrations**: follow `docs/modelos-y-migraciones.md`.
  - Always commit the model change and its migration together.
  - Review generated migrations before applying (renames can show up as drop + create).
  - Never edit or delete a migration that was already shared; create a new one.
  - Ruff excludes `migrations/versions`.
- **Passwords**: store only argon2id hashes (`PasswordHasher().hash`); never store or log plaintext.
- **Queries**: use SQLAlchemy 2.0 style (`db.session.scalar(select(Model).where(...))`), not the legacy `Model.query` API.
- **Language**: code, identifiers, UI copy and commit messages in English; `docs/` and the README are in Spanish.

## Testing

- `TestingConfig` uses in-memory SQLite; tables are created/dropped per test with `db.create_all()` / `db.drop_all()` (no migrations in tests).
- Fixtures (`tests/conftest.py`):
  - `app` (session scope)
  - `client` (Flask test client)
  - `init_database` (creates/drops tables)
  - `session` (`db.session` inside an app context)
- Request a fixture that depends on `init_database` (e.g. `session`) whenever a test touches the DB.
- Test through the public interface (HTTP via `client`), then assert persisted state through `session`.
- Add tests alongside every behavior change.

## Git workflow

- Branches are named after the GitHub issue: `<issue-number>-<short-name>` (e.g. `3-user-register`).
- Commit messages: imperative summary ending with the issue reference, e.g. `Add user blueprint & migration. Ref #3`.
- Changes reach `main` through pull requests.
- Do not commit `.env`; copy `.env.example` and fill in `SECRET_KEY`.

## Design notes

`docs/justificacion-patrones.md` documents the planned domain patterns:

- **Factory Method** for answer authors (human user vs. AI agent).
- **Strategy** for pluggable LLM providers (`generate(prompt)`).

Keep new domain code consistent with these decisions.
