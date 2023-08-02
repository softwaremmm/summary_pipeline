from summary import summarise
from pathlib import Path


def test_regression(test_set: dict):
    summary = summarise.create_summary(
        test_set["gatekeeper_report"],
        test_set["competitivemapping_report"],
        test_set["mykrobe_report"],
        test_set["gnomonicus"],
    )

    expected_summary = summarise.read_json_file(test_set["expected_output"])

    assert summary == expected_summary
