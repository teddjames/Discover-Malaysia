# Deploy Discover Malaysia on Render

This package was built from your uploaded `discover_malaysia(1).zip` and keeps its original travel pages, code, and photos.

## GitHub

1. Extract this archive.
2. Upload the **contents** of the `discover_malaysia` directory to the root of a GitHub repository (not the containing folder).
3. The repository root must contain `app.py`, `render.yaml`, `requirements.txt`, `.python-version`, `database/`, `static/`, and `templates/`.
4. Do not upload `.git` or `database/tourism.db`. The application creates the database automatically at startup.

## Render — recommended

1. Visit https://dashboard.render.com and select New > Blueprint.
2. Connect your GitHub repository; Render reads `render.yaml`.
3. Select your repository and deploy the free web service.
4. When deployment succeeds, visit the `onrender.com` link provided by Render.

## Render — manual Web Service alternative

- Runtime: Python 3
- Root directory: blank, assuming the repository root contains `app.py`
- Build: `pip install -r requirements.txt`
- Start: `python database/seed_db.py && gunicorn app:app --workers 1 --bind 0.0.0.0:$PORT --timeout 120`
- Instance type: Free (for a demonstration project)

The `.python-version` file chooses a compatible Python 3.12 release.

## Database limitations

The free Render service filesystem is ephemeral. The SQLite database is created and seeded at **each app start** to make this read-only travel guide usable after restarts. Do not use this arrangement for persistent user accounts, saved itineraries, reservations, payments, or user-submitted content. For those features, migrate to managed PostgreSQL.

## Testing

- `python database/seed_db.py`
- `python -m unittest discover -s tests -v` (after dependencies are installed)
- `python app.py` for local development

Check the licensing/usage rights of your supplied destination photographs before publishing them. No deployment to Render was performed here.
