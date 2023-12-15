import json
from pathlib import Path
from summary import summarise


def test_regression(regression_test_set: dict):
    test_reports = {}
    if "PIPELINE_BUILD" in regression_test_set:
        test_reports["versions"] = regression_test_set["PIPELINE_BUILD"]
    if "knowledge" in regression_test_set:
        test_reports["knowledge"] = regression_test_set["knowledge"]
    test_reports["gatekeeper"] = regression_test_set["gatekeeper_report"]
    if "competitivemapping_report" in regression_test_set:
        test_reports["mapping"] = regression_test_set["competitivemapping_report"]
    if "mykrobe_report" in regression_test_set:
        test_reports["mykrobe"] = regression_test_set["mykrobe_report"]
    if "clockwork_report" in regression_test_set:
        test_reports["clockwork"] = regression_test_set["clockwork_report"]
    if "gnomonicus" in regression_test_set:
        test_reports["gnomonicus"] = regression_test_set["gnomonicus"]
    if "name_mapping" in regression_test_set:
        test_reports["name_mapping"] = regression_test_set["name_mapping"]

    summary = summarise.create_summary(test_reports)

    with open(regression_test_set["expected_output"], "r") as file:
        expected_summary = json.load(file)

    assert summary == expected_summary
