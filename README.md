# ETHEREAL BUBBLES 🫧

#### Video Demo: TODO
#### Live Application: https://ethereal-production-production.up.railway.app\n
## Description

**ETHEREAL Universe** is a web-based application created as my CS50 final project. It extends ETHEREAL, my existing digital education brand, with a small interactive account system while keeping the published public website visually unchanged.

The public ETHEREAL website is designed as an editorial entrance to six knowledge worlds: Nutrition, Era, Mind, Finance, Living, and Career. The purpose of this final project is not to rebuild that website. Instead, this application gives visitors a personal space inside ETHEREAL. A user can create an account, sign in, remain authenticated between requests, choose favorite ETHEREAL worlds, save them to a collection called **My Bubbles**, remove bubbles later, and log out.

The project deliberately has a focused scope. I wanted the final application to solve one simple problem well: a visitor who discovers parts of ETHEREAL that interest them should have a way to keep those interests associated with their own account. This also allowed me to apply the web concepts introduced throughout CS50 without adding unrelated features merely to make the project larger.

## How it works

The application uses **Python with Flask** for the server-side logic. Flask defines the routes for the homepage, registration, login, logout, My Bubbles page, health check, and the small JSON endpoint used to save or remove bubbles.

When a user creates an account, their name and email address are stored in SQLite. Their password is never stored directly. Werkzeug's password-hashing functions create a secure password hash, and login attempts are checked against that hash.

After successful registration or login, Flask stores the user's numeric ID in a session. Routes such as `/my-bubbles` and the bubble-saving endpoint require an authenticated session. If an unauthenticated visitor tries to open a protected route, the application redirects them to the login page.

The six ETHEREAL worlds are stored in a `bubbles` SQL table. A separate `user_bubbles` table connects users to the bubbles they have saved. This creates a many-to-many relationship: one user may save several bubbles, and the same bubble may be saved by many different users.

The My Bubbles page shows all six worlds and indicates which ones belong to the current user's collection. When the user selects **Save bubble** or removes a saved bubble, JavaScript sends an asynchronous POST request to Flask. Flask updates the SQL relationship and sends a JSON response back to the browser. JavaScript then updates the button immediately without reloading the page.

## Project files

### `app.py`

This is the main Flask application. It contains the application configuration, database connection helper, account registration and login logic, Flask session handling, route protection, My Bubbles queries, the save/remove API endpoint, a health-check endpoint, and security-related response headers.

The application uses environment variables for production settings. A production deployment must provide a secret key instead of relying on the local development fallback. When deployed on Railway, the application also detects Railway's persistent volume mount path and stores the SQLite database there.

### `schema.sql`

This file defines the three SQL tables used by the application:

- `users` stores account information and password hashes.
- `bubbles` stores the six ETHEREAL knowledge worlds.
- `user_bubbles` stores the relationship between a user and a saved bubble.

The schema also inserts the six default ETHEREAL worlds with `INSERT OR IGNORE`, allowing the application to initialize safely without duplicating them.

### `templates/`

The Jinja templates contain the HTML rendered by Flask.

- `layout.html` contains the shared page structure and navigation.
- `index.html` introduces the ETHEREAL Universe application.
- `register.html` provides the account-creation form.
- `login.html` provides the sign-in form.
- `my_bubbles.html` displays the six worlds and the current user's saved state.

### `static/css/styles.css`

This contains the application's visual design. I wanted the final project to feel related to ETHEREAL without modifying the existing public website. It therefore uses the brand's dark editorial appearance, serif typography, soft atmospheric light, and translucent bubble-inspired elements.

### `static/js/app.js`

This JavaScript handles the save/remove interaction. It listens for clicks on bubble buttons, sends an HTTP POST request with `fetch()`, reads the JSON response, and changes the interface between **Save bubble** and **Saved** without a page refresh.

### `requirements.txt`, `Procfile`, and `railway.json`

These files prepare the project for deployment. The application uses Gunicorn as its production web server. The Railway configuration specifies the production start command and the `/health` health-check endpoint.

### `tests/test_app.py`

The automated test exercises the application's central workflow. It checks the health endpoint, creates an account, verifies that the stored password is a hash rather than plaintext, saves a bubble, logs out, confirms that My Bubbles becomes protected, and signs back in.

The GitHub Actions workflow in `.github/workflows/tests.yml` installs the dependencies and runs this test automatically.

## Design decisions

One important design decision was to keep ETHEREAL's existing public site separate from the Flask application. Rebuilding the public site would have duplicated work and risked changing an experience that already existed. Instead, the final architecture treats the public site as the entrance and the Flask project as the interactive account layer.

The existing **Explore the Universe** button on the public ETHEREAL website opens the deployed Railway application in a new tab. The appearance and layout of the public website remain unchanged; only the destination of that button changes.

I also chose SQLite rather than a more complex database server because the data model is intentionally small and relational, and SQLite directly demonstrates the SQL concepts used in CS50. In production, the database file is placed on persistent storage so account and My Bubbles data survive redeployments.

Finally, I intentionally did not add search, artificial intelligence, payments, social networking, or a large dashboard. Those features were not necessary to solve the problem this project addresses. The final project is meant to be understandable, complete, and useful rather than large for its own sake.

## Running locally

Install the dependencies:

```bash
pip install -r requirements.txt
```

Initialize the database:

```bash
flask --app app init-db
```

Run the development server:

```bash
flask --app app run
```

Before CS50 submission, the Video Demo URL above will be replaced with the final video link.

Deployment is configured through Railway from the `main` branch. Production uses Gunicorn, a Railway health check, and a persistent volume mounted at `/data` for SQLite.
