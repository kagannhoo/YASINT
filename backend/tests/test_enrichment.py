from app.utils.enrichment import extract_seeds, has_new_seeds, merge_into_inputs, normalize_username


def test_normalize_username():
    assert normalize_username("@kaganhoo") == "kaganhoo"


def test_extract_emails_from_findings():
    findings = [
        {
            "module": "social",
            "key": "email_found",
            "value": "test@example.com",
            "raw_data": None,
        },
        {
            "module": "username",
            "key": "account_github",
            "value": "https://github.com/kaganhoo",
            "raw_data": None,
        },
    ]
    seeds = extract_seeds(findings, {"username": "kaganhoo"})
    assert "test@example.com" in seeds["emails"]
    assert "https://github.com/kaganhoo" in seeds["urls"]


def test_merge_discovers_new_email():
    base = {"username": "kaganhoo"}
    seeds = {
        "emails": ["found@mail.com"],
        "usernames": ["kaganhoo"],
        "urls": ["https://github.com/kaganhoo"],
        "ips": [],
    }
    merged = merge_into_inputs(base, seeds)
    assert merged["email"] == "found@mail.com"
    assert has_new_seeds(base, merged) is True
