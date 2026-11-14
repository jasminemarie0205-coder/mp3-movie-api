def test_upload_csv(client, sample_csv_bytes):
    response = client.post(
        "/upload",
        files={"file": ("sample_movies.csv", sample_csv_bytes, "text/csv")},
    )
    assert response.status_code == 200
    assert response.json() == {
        "filename": "sample_movies.csv",
        "rows": 20,
        "columns": 4,
        "column_names": ["title", "release_year", "rating", "genre"],
    }


def test_upload_twice_replaces_movies(client, sample_csv_bytes):
    for _ in range(2):
        response = client.post(
            "/upload",
            files={"file": ("sample_movies.csv", sample_csv_bytes, "text/csv")},
        )
        assert response.status_code == 200

    response = client.get("/movies")
    assert response.json()["total_rows"] == 20


def test_upload_unsupported_extension(client):
    response = client.post(
        "/upload",
        files={"file": ("notes.txt", b"hello", "text/plain")},
    )
    assert response.status_code == 400

    response = client.get("/health")
    assert response.status_code == 200


def test_get_movies_with_limit(client, uploaded_movies):
    response = client.get("/movies", params={"limit": 2})
    assert response.status_code == 200
    assert response.json() == {
        "data": [
            {"id": 1, "title": "Movie A", "release_year": 2020, "rating": 8.0, "genre": "Drama"},
            {"id": 2, "title": "Movie B", "release_year": 2021, "rating": 8.5, "genre": "Comedy"},
        ],
        "total_rows": 20,
    }


def test_get_movies_empty(client):
    response = client.get("/movies")
    assert response.status_code == 200
    assert response.json() == {"data": [], "total_rows": 0}


def test_search_movies(client, uploaded_movies):
    response = client.get("/movies/search", params={"min_rating": 8.5, "limit": 2})
    assert response.status_code == 200
    assert response.json() == [
        {"id": 4, "title": "Movie C"},
        {"id": 2, "title": "Movie B"},
    ]

    response = client.get(
        "/movies/search",
        params={"columns": ["title", "rating"], "min_rating": 8.5, "limit": 2},
    )
    assert response.status_code == 200
    assert response.json() == [
        {"id": 4, "title": "Movie C", "rating": 9.0},
        {"id": 2, "title": "Movie B", "rating": 8.5},
    ]


def test_search_unsupported_column(client, uploaded_movies):
    response = client.get("/movies/search", params={"columns": ["budget"]})
    assert response.status_code == 400


def test_process_and_retrieve(client, uploaded_movies, processing_body):
    response = client.post("/movies/process", json=processing_body)
    assert response.status_code == 200
    report = response.json()
    assert report["validation_rows_removed"] == 0
    assert report["cleaning_report"]["rows_before"] == 20
    assert report["cleaning_report"]["rows_after"] == 18

    response = client.get("/movies")
    body = response.json()
    assert body["total_rows"] == 18
    titles = [row["title"] for row in body["data"]]
    assert len(titles) == len(set(titles))


def test_process_with_no_movies(client, processing_body):
    response = client.post("/movies/process", json=processing_body)
    assert response.status_code == 400