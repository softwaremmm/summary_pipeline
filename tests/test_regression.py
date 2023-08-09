from summary import summarise
from summary.reports import ReportList, ReportType, Report
from pathlib import Path


def test_regression(regression_test_set: dict):
    test_reports = ReportList(
        [
            Report(ReportType.GATEKEEPER, regression_test_set["gatekeeper_report"]),
            Report(
                ReportType.MAPPING, regression_test_set["competitivemapping_report"]
            ),
            Report(ReportType.MYKROBE, regression_test_set["mykrobe_report"]),
            Report(ReportType.GNOMONICUS, regression_test_set["gnomonicus"]),
        ]
    )

    summary = summarise.create_summary(test_reports)

    expected_summary = summarise.read_json_file(regression_test_set["expected_output"])

    assert summary == expected_summary
