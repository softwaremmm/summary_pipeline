import json


def test_coverage(regression_test_set: dict):
    """
    This test is intended to ensure that the first coverage result reported in the
    summary is always the coverage of the top hit from competitive mapping.
    """

    if "competitivemapping_report" in regression_test_set:
        with open(regression_test_set["competitivemapping_report"], "r") as file:
            competitivemapping_report = json.load(file)

        with open(regression_test_set["expected_output"], "r") as file:
            expected_summary = json.load(file)

        assert (
            competitivemapping_report["references"][0]["coverage"]
            == expected_summary["Mycobacterium Results"]["Summary"][0]["Coverage"]
        )


def test_depth(regression_test_set: dict):
    """
    This test is intended to ensure that the first coverage result reported in the
    summary is always the coverage of the top hit from competitive mapping.
    """

    if "competitivemapping_report" in regression_test_set:
        with open(regression_test_set["competitivemapping_report"], "r") as file:
            competitivemapping_report = json.load(file)

        with open(regression_test_set["expected_output"], "r") as file:
            expected_summary = json.load(file)

        assert (
            competitivemapping_report["references"][0]["meandepth"]
            == expected_summary["Mycobacterium Results"]["Summary"][0]["Depth"]
        )
