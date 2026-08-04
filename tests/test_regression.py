import json

from summary import summarise

OVERWRITE_EXPECTED_OUTPUT = False


def test_regression(regression_test_set: dict):
    test_reports = summarise.report_list_to_dict(list(regression_test_set.values()))

    summary = summarise.create_summary(test_reports)

    with open(regression_test_set["expected_output"], "r", encoding="utf-8") as file:
        expected_summary = json.load(file)

    if summary != expected_summary:
        outfile = (
            regression_test_set["expected_output"]
            if OVERWRITE_EXPECTED_OUTPUT
            else regression_test_set["expected_output"] + ".test_output"
        )

        with open(outfile, "w", encoding="utf-8") as file:
            json.dump(summary, file, indent=4)

    assert summary == expected_summary
