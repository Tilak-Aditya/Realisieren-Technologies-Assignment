from processing.validation import validate_record


def valid_book():
    return {
        "source": "Books to Scrape",
        "source_url": "https://books.toscrape.com/catalogue/example/index.html",
        "name_or_title": "Example Book",
        "category": None,
        "price": 10.50,
        "rating": 4,
        "author": None,
        "tags": None,
        "description": None,
        "scraped_at": "2026-10-07T00:00:00+00:00",
    }


def test_valid_book_has_no_problems():
    assert validate_record(valid_book()) == []


def test_missing_name_is_rejected():
    record = valid_book()
    record["name_or_title"] = None
    assert "missing_name" in validate_record(record)


def test_invalid_price_is_rejected():
    record = valid_book()
    record["price"] = -1
    assert "invalid_price" in validate_record(record)


def test_invalid_rating_is_rejected():
    record = valid_book()
    record["rating"] = 6
    assert "invalid_rating" in validate_record(record)


def test_unknown_source_is_rejected():
    record = valid_book()
    record["source"] = "Unknown Source"
    assert "unknown_source" in validate_record(record)
