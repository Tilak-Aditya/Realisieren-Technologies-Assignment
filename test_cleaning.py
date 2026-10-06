from processing.cleaning import (
    clean_price,
    clean_rating,
    clean_tags,
    clean_text,
    normalize_url,
    strip_quotes,
)


def test_clean_text_collapses_whitespace():
    assert clean_text("  Hello \n World \xa0 Test ") == "Hello World Test"


def test_strip_quotes():
    assert strip_quotes("“A useful quote”") == "A useful quote"


def test_clean_price():
    assert clean_price("£51.77") == 51.77


def test_clean_rating():
    assert clean_rating("star-rating Three") == 3


def test_clean_tags():
    assert clean_tags([" Technology ", "life", "technology"]) == "life;technology"


def test_normalize_url():
    assert normalize_url(" https://example.com/path ") == "https://example.com/path"


def test_invalid_url_becomes_none():
    assert normalize_url("not-a-url") is None
