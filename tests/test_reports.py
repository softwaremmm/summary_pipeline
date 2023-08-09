from pathlib import Path
import pytest
from summary.reports import Report, ReportList, ReportType


def test_gatekeeper_report(
    eg_gatekeeper_report: Path, eg_gatekeeper_report_contents: dict
):
    report = Report(
        ReportType.GATEKEEPER,
        eg_gatekeeper_report,
    )
    assert report.report_type == ReportType.GATEKEEPER
    assert report.report_path == eg_gatekeeper_report
    assert report.report_contents == eg_gatekeeper_report_contents


def test_competitivemapping_report(
    eg_competitivemapping_report: Path, eg_competitivemapping_report_contents: dict
):
    report = Report(
        ReportType.MAPPING,
        eg_competitivemapping_report,
    )
    assert report.report_type == ReportType.MAPPING
    assert report.report_path == eg_competitivemapping_report
    assert report.report_contents == eg_competitivemapping_report_contents


def test_mykrobe_report(eg_mykrobe_report: Path, eg_mykrobe_report_contents: dict):
    report = Report(
        ReportType.MYKROBE,
        eg_mykrobe_report,
    )
    assert report.report_type == ReportType.MYKROBE
    assert report.report_path == eg_mykrobe_report
    assert report.report_contents == eg_mykrobe_report_contents


def test_gnomonicus_report(
    eg_gnomonicus_report: Path, eg_gnomonicus_report_contents: dict
):
    report = Report(
        ReportType.GNOMONICUS,
        eg_gnomonicus_report,
    )
    assert report.report_type == ReportType.GNOMONICUS
    assert report.report_path == eg_gnomonicus_report
    assert report.report_contents == eg_gnomonicus_report_contents


def test_retrieve_report(
    report_set_four: ReportList,
    eg_gnomonicus_report: Path,
    eg_gnomonicus_report_contents: dict,
):
    report = report_set_four.retrieve(ReportType.GNOMONICUS)

    assert report.report_type == ReportType.GNOMONICUS
    assert report.report_path == eg_gnomonicus_report
    assert report.report_contents == eg_gnomonicus_report_contents


def test_check_for_report(report_set_four: ReportList):
    assert report_set_four.contains(ReportType.MAPPING)


def test_report_list_string(report_set_four: ReportList):
    assert (
        str(report_set_four)
        == "[PosixPath('test_data/example_input/WTCHG_885333_73225298_1/52/gatekeeper_report.json'), PosixPath('test_data/example_input/WTCHG_885333_73225298_1/52/competitivemapping_report.json'), PosixPath('test_data/example_input/WTCHG_885333_73225298_1/52/mykrobe_report.json'), PosixPath('test_data/example_input/WTCHG_885333_73225298_1/52/tb/gnomonicus.json')]"
    )


def test_report_missing(report_set_three: ReportList):
    with pytest.raises(ValueError):
        report = report_set_three.retrieve(ReportType.GNOMONICUS)
