import json
import pytest
from pathlib import Path

from summary.reports import Report, ReportList, ReportType


WTCHG_885333_73225298_1_1 = {
    "gatekeeper_report": "test_data/example_input/WTCHG_885333_73225298_1/1/gatekeeper_report.json",
    "competitivemapping_report": "test_data/example_input/WTCHG_885333_73225298_1/1/competitivemapping_report.json",
    "mykrobe_report": "test_data/example_input/WTCHG_885333_73225298_1/1/mykrobe_report.json",
    "gnomonicus": "test_data/example_input/WTCHG_885333_73225298_1/1/tb/gnomonicus.json",
    "expected_output": "test_data/example_output/WTCHG_885333_73225298_1/1/Mega_1.json",
}

WTCHG_885333_73225298_1_2 = {
    "gatekeeper_report": "test_data/example_input/WTCHG_885333_73225298_1/2/gatekeeper_report.json",
    "competitivemapping_report": "test_data/example_input/WTCHG_885333_73225298_1/2/competitivemapping_report.json",
    "mykrobe_report": "test_data/example_input/WTCHG_885333_73225298_1/2/mykrobe_report.json",
    "gnomonicus": "test_data/example_input/WTCHG_885333_73225298_1/2/tb/gnomonicus.json",
    "expected_output": "test_data/example_output/WTCHG_885333_73225298_1/2/Mega_2.json",
}

WTCHG_885333_73225298_1_52 = {
    "gatekeeper_report": "test_data/example_input/WTCHG_885333_73225298_1/52/gatekeeper_report.json",
    "competitivemapping_report": "test_data/example_input/WTCHG_885333_73225298_1/52/competitivemapping_report.json",
    "mykrobe_report": "test_data/example_input/WTCHG_885333_73225298_1/52/mykrobe_report.json",
    "gnomonicus": "test_data/example_input/WTCHG_885333_73225298_1/52/tb/gnomonicus.json",
    "expected_output": "test_data/example_output/WTCHG_885333_73225298_1/52/main_report.json",
}


@pytest.fixture(
    params=[
        WTCHG_885333_73225298_1_1,
        WTCHG_885333_73225298_1_2,
        WTCHG_885333_73225298_1_52,
    ]
)
def regression_test_set(request) -> dict:
    return request.param


@pytest.fixture
def all_reports_set_individually() -> list:
    return [
        "--gatekeeper",
        "test_data/example_input/WTCHG_885333_73225298_1/2/gatekeeper_report.json",
        "--mapping",
        "test_data/example_input/WTCHG_885333_73225298_1/2/competitivemapping_report.json",
        "--mykrobe",
        "test_data/example_input/WTCHG_885333_73225298_1/2/mykrobe_report.json",
        "--gnomonicus",
        "test_data/example_input/WTCHG_885333_73225298_1/2/tb/gnomonicus.json",
    ]


@pytest.fixture
def four_reports() -> list:
    return [
        "--reports",
        "test_data/example_input/WTCHG_885333_73225298_1/2/gatekeeper_report.json",
        "test_data/example_input/WTCHG_885333_73225298_1/2/competitivemapping_report.json",
        "test_data/example_input/WTCHG_885333_73225298_1/2/mykrobe_report.json",
        "test_data/example_input/WTCHG_885333_73225298_1/2/tb/gnomonicus.json",
    ]


@pytest.fixture
def three_reports() -> list:
    return [
        "--reports",
        "test_data/example_input/WTCHG_885333_73225298_1/2/gatekeeper_report.json",
        "test_data/example_input/WTCHG_885333_73225298_1/2/competitivemapping_report.json",
        "test_data/example_input/WTCHG_885333_73225298_1/2/mykrobe_report.json",
    ]


@pytest.fixture
def one_report() -> list:
    return [
        "--reports",
        "test_data/example_input/WTCHG_885333_73225298_1/2/gatekeeper_report.json",
    ]


@pytest.fixture
def bad_report_combination() -> list:
    return [
        "--reports",
        "test_data/example_input/WTCHG_885333_73225298_1/2/gatekeeper_report.json",
        "test_data/example_input/WTCHG_885333_73225298_1/2/tb/gnomonicus.json",
    ]


@pytest.fixture
def no_reports() -> list:
    return ["--reports"]


@pytest.fixture
def bad_reports() -> list:
    return ["--bad", "bad"]


@pytest.fixture
def eg_gatekeeper_report() -> Path:
    return Path(
        "test_data/example_input/WTCHG_885333_73225298_1/52/gatekeeper_report.json"
    )


@pytest.fixture
def eg_gatekeeper_report_contents(eg_gatekeeper_report) -> dict:
    with open(eg_gatekeeper_report, "r") as file:
        return json.load(file)


@pytest.fixture
def eg_competitivemapping_report() -> Path:
    return Path(
        "test_data/example_input/WTCHG_885333_73225298_1/52/competitivemapping_report.json"
    )


@pytest.fixture
def eg_competitivemapping_report_contents(eg_competitivemapping_report) -> dict:
    with open(eg_competitivemapping_report, "r") as file:
        return json.load(file)


@pytest.fixture
def eg_mykrobe_report() -> Path:
    return Path(
        "test_data/example_input/WTCHG_885333_73225298_1/52/mykrobe_report.json"
    )


@pytest.fixture
def eg_mykrobe_report_contents(eg_mykrobe_report) -> dict:
    with open(eg_mykrobe_report, "r") as file:
        return json.load(file)


@pytest.fixture
def eg_gnomonicus_report() -> Path:
    return Path("test_data/example_input/WTCHG_885333_73225298_1/52/tb/gnomonicus.json")


@pytest.fixture
def eg_gnomonicus_report_contents(eg_gnomonicus_report) -> dict:
    with open(eg_gnomonicus_report, "r") as file:
        return json.load(file)


@pytest.fixture
def report_set_one(
    eg_gatekeeper_report,
) -> ReportList:
    return ReportList(
        [
            Report(ReportType.GATEKEEPER, eg_gatekeeper_report),
        ]
    )


@pytest.fixture
def report_set_three(
    eg_gatekeeper_report,
    eg_competitivemapping_report,
    eg_mykrobe_report,
) -> ReportList:
    return ReportList(
        [
            Report(ReportType.GATEKEEPER, eg_gatekeeper_report),
            Report(ReportType.MAPPING, eg_competitivemapping_report),
            Report(ReportType.MYKROBE, eg_mykrobe_report),
        ]
    )


@pytest.fixture
def report_set_four(
    eg_gatekeeper_report,
    eg_competitivemapping_report,
    eg_mykrobe_report,
    eg_gnomonicus_report,
) -> ReportList:
    return ReportList(
        [
            Report(ReportType.GATEKEEPER, eg_gatekeeper_report),
            Report(ReportType.MAPPING, eg_competitivemapping_report),
            Report(ReportType.MYKROBE, eg_mykrobe_report),
            Report(ReportType.GNOMONICUS, eg_gnomonicus_report),
        ]
    )


@pytest.fixture
def report_set_bad(
    eg_gnomonicus_report,
) -> ReportList:
    return ReportList(
        [
            Report(ReportType.GNOMONICUS, eg_gnomonicus_report),
        ]
    )
