# MP3 Movie API

For MP3 I took my MP2 API and made it save movies in a SQLite database instead of just keeping them in memory. You upload a CSV of movies (title, release_year, rating, genre) to `/upload`, and it replaces whatever was in the database before. `database.py` makes the movies table and `storage.py` has all the SQL queries, so the movies are still there even if you restart the server. The `/movies/process` endpoint uses my data pipeline from MP1 to clean the movies (removing duplicates, missing values, and outliers) and then saves the cleaned version back into the database. I also added caching for `GET /movies` using fakeredis in `cache.py`, so if you ask for the same limit twice, the second one comes from the cache and doesn't touch the database. Any time the data changes from an upload or processing, the cache gets cleared so it doesn't give back old results. Search (`/movies/search`) filters by rating with SQL and isn't cached. `models.py` has the response models and `middleware.py` logs the requests.

## Setup

```bash
python -m venv venv
venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Start the API

```bash
python -m uvicorn main:app --reload
```

Then open http://127.0.0.1:8000/docs.

## Run the tests

```bash
python -m pytest tests -v
```

## Sample processing request

To try processing, upload `fixtures/sample_movies.csv` first, then send this to `POST /movies/process`:

```json
{
  "validation": {
    "required_columns": ["title", "release_year", "rating", "genre"],
    "numeric_columns": ["release_year", "rating"]
  },
  "processing": {
    "remove_duplicates": true,
    "missing": {"enabled": true, "axis": "rows"},
    "outliers": {
      "enabled": true,
      "columns": ["rating"],
      "method": "iqr",
      "threshold": 1.5
    }
  }
}
```

You should get this back:

```json
{
  "validation_rows_removed": 0,
  "cleaning_report": {
    "rows_before": 20,
    "rows_after": 16,
    "rows_removed": 4,
    "columns_before": 4,
    "columns_after": 4,
    "columns_removed": 0
  }
}
```

It drops 4 rows total: the duplicate Movie B and Movie D, plus Movie Q and Movie R since their ratings (1.0 and 0.5) count as outliers.