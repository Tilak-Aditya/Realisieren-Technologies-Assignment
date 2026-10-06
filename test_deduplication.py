from processing.deduplication import find_duplicates, make_fingerprint


def test_book_duplicates_ignore_case_and_spaces():
    records = [
        {
            "source": "Books to Scrape",
            "name_or_title": "Example Book Title",
        },
        {
            "source": "Books to Scrape",
            "name_or_title": "  Example Book Title ",
        },
        {
            "source": "Books to Scrape",
            "name_or_title": "EXAMPLE BOOK TITLE",
        },
    ]

    unique, duplicates = find_duplicates(records)

    assert len(unique) == 1
    assert len(duplicates) == 2


def test_quote_fingerprint_uses_source_author_and_first_50_chars():
    first = {
        "source": "Quotes to Scrape",
        "author": "Jane Doe",
        "name_or_title": "A quote that is sufficiently long for this test.",
    }
    second = {
        "source": "Quotes to Scrape",
        "author": " jane doe ",
        "name_or_title": "A QUOTE THAT IS SUFFICIENTLY LONG FOR THIS TEST.",
    }

    assert make_fingerprint(first) == make_fingerprint(second)
