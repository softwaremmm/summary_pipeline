import json
import pytest
from pathlib import Path

from summary.cli_args import Arguments

SRR2097047 = {
    "gatekeeper_report": "test_data/SRR2097047/gatekeeper_report.json",
    "expected_output": "test_data/SRR2097047/main_report.json",
}

abscessus = {
    "gatekeeper_report": "test_data/abscessus/gatekeeper_report.json",
    "competitivemapping_report": "test_data/abscessus/competitivemapping_report.json",
    "mykrobe_report": "test_data/abscessus/mykrobe_report.json",
    "expected_output": "test_data/abscessus/main_report.json",
}

WTCHG_885333_73205296_1 = {
    "gatekeeper_report": "test_data/WTCHG_885333_73205296_1/gatekeeper_report.json",
    "competitivemapping_report": "test_data/WTCHG_885333_73205296_1/competitivemapping_report.json",
    "mykrobe_report": "test_data/WTCHG_885333_73205296_1/mykrobe_report.json",
    "gnomonicus": "test_data/WTCHG_885333_73205296_1/tb/gnomonicus.json",
    "expected_output": "test_data/WTCHG_885333_73205296_1/main_report.json",
}


@pytest.fixture(
    params=[
        SRR2097047,
        abscessus,
        WTCHG_885333_73205296_1,
    ]
)
def regression_test_set(request) -> dict:
    return request.param


@pytest.fixture
def all_reports_set_individually() -> list:
    return [
        "--gatekeeper",
        "test_data/WTCHG_885333_73205296_1/gatekeeper_report.json",
        "--mapping",
        "test_data/WTCHG_885333_73205296_1/competitivemapping_report.json",
        "--mykrobe",
        "test_data/WTCHG_885333_73205296_1/mykrobe_report.json",
        "--gnomonicus",
        "test_data/WTCHG_885333_73205296_1/tb/gnomonicus.json",
    ]


@pytest.fixture
def all_reports_set_individually_args(all_reports_set_individually) -> Arguments:
    return Arguments(all_reports_set_individually)


@pytest.fixture
def four_reports() -> list:
    return [
        "--reports",
        "test_data/WTCHG_885333_73205296_1/gatekeeper_report.json",
        "test_data/WTCHG_885333_73205296_1/competitivemapping_report.json",
        "test_data/WTCHG_885333_73205296_1/mykrobe_report.json",
        "test_data/WTCHG_885333_73205296_1/tb/gnomonicus.json",
    ]


@pytest.fixture
def four_reports_args(four_reports) -> Arguments:
    return Arguments(four_reports)


@pytest.fixture
def three_reports() -> list:
    return [
        "--reports",
        "test_data/WTCHG_885333_73205296_1/gatekeeper_report.json",
        "test_data/WTCHG_885333_73205296_1/competitivemapping_report.json",
        "test_data/WTCHG_885333_73205296_1/mykrobe_report.json",
    ]


@pytest.fixture
def one_report() -> list:
    return [
        "--reports",
        "test_data/WTCHG_885333_73205296_1/gatekeeper_report.json",
    ]


@pytest.fixture
def bad_report_combination() -> list:
    return [
        "--reports",
        "test_data/WTCHG_885333_73205296_1/gatekeeper_report.json",
        "test_data/WTCHG_885333_73205296_1/tb/gnomonicus.json",
    ]


@pytest.fixture
def no_reports() -> list:
    return ["--reports"]


@pytest.fixture
def bad_reports() -> list:
    return ["--bad", "bad"]


@pytest.fixture
def eg_gatekeeper_report() -> Path:
    return Path("test_data/WTCHG_885333_73205296_1/52/gatekeeper_report.json")


@pytest.fixture
def eg_gatekeeper_report_contents(eg_gatekeeper_report) -> dict:
    with open(eg_gatekeeper_report, "r") as file:
        return json.load(file)


@pytest.fixture
def eg_competitivemapping_report() -> Path:
    return Path("test_data/WTCHG_885333_73205296_1/52/competitivemapping_report.json")


@pytest.fixture
def eg_competitivemapping_report_contents(eg_competitivemapping_report) -> dict:
    with open(eg_competitivemapping_report, "r") as file:
        return json.load(file)


@pytest.fixture
def eg_mykrobe_report() -> Path:
    return Path("test_data/WTCHG_885333_73205296_1/52/mykrobe_report.json")


@pytest.fixture
def eg_mykrobe_report_contents(eg_mykrobe_report) -> dict:
    with open(eg_mykrobe_report, "r") as file:
        return json.load(file)


@pytest.fixture
def eg_gnomonicus_report() -> Path:
    return Path("test_data/WTCHG_885333_73205296_1/52/tb/gnomonicus.json")


@pytest.fixture
def eg_gnomonicus_report_contents(eg_gnomonicus_report) -> dict:
    with open(eg_gnomonicus_report, "r") as file:
        return json.load(file)
