# START_APP.md — how to run and probe this app

> **Build team:** fill in every `<...>` below once your app runs. Other teams use this file to
> start your app and probe it during Break. Keep it accurate — a break is filed against the app a
> breaker can actually start from these instructions.

## What this app is

- **App:** a blog + comments board (menu #4) — read posts, leave comments, admin writes posts/drafts.
- **Stack:** Python + Flask + SQLite (file-based, `blog.db`, created on first run).

## Start it

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run it
flask --app app run --port 8000
```

- **Base URL:** http://localhost:8000
- **Stop it:** Ctrl-C in the terminal running it.

## How to interact with it

- **Main endpoints / pages:**
  - `GET /` — home page listing published posts.
  - `GET /post/<id>` — view a single post and its comments — e.g. `http://localhost:8000/post/1`
  - `POST /post/<id>/comment` — add a comment (form fields `author`, `body`).
  - `GET /login`, `POST /login` — admin login (form fields `username`, `password`).
  - `GET /admin` — admin dashboard (create posts, see drafts); requires login.
  - `POST /admin/new` — create a post (form fields `title`, `body`, optional `published`).
  - `GET /logout` — end the admin session.
- **Accounts / credentials for legitimate use:** none needed to read posts or comment. The admin
  login is private to the build team (breakers are not given it).
- **A benign request that should succeed:**

  ```bash
  curl http://localhost:8000/post/1
  ```

## For breakers

Attack this **running app over HTTP** — do **not** read this repo's source or `secret/` to find a
break. See [AGENTS_BREAK.md](AGENTS_BREAK.md) for the rules and your AI agent's instructions, and
[SPEC.md](SPEC.md) for the five properties (P1–P5) you are probing for.
