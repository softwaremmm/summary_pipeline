import json
import pytest
from pathlib import Path

from summary.cli_args import Arguments

covid = {
    "gatekeeper_report": "test_data/covid/speciation_report.json",
    "expected_output": "test_data/covid/main_report.json",
}

SRR2097047 = {
    "gatekeeper_report": "test_data/SRR2097047/speciation_report.json",
    "expected_output": "test_data/SRR2097047/main_report.json",
}

NTM = {
    "gatekeeper_report": "test_data/NTM/speciation_report.json",
    "competitivemapping_report": "test_data/NTM/competitivemapping_report.json",
    "mykrobe_report": "test_data/NTM/subspecies_report.json",
    "expected_output": "test_data/NTM/main_report.json",
}

WTCHG_885333_73205296_1 = {
    "gatekeeper_report": "test_data/WTCHG_885333_73205296_1/speciation_report.json",
    "competitivemapping_report": "test_data/WTCHG_885333_73205296_1/competitivemapping_report.json",
    "mykrobe_report": "test_data/WTCHG_885333_73205296_1/subspecies_report.json",
    "clockwork_report": "test_data/WTCHG_885333_73205296_1/genome_creation_report.json",
    "gnomonicus": "test_data/WTCHG_885333_73205296_1/tb/resistance_prediction_report.json",
    "expected_output": "test_data/WTCHG_885333_73205296_1/main_report.json",
}

clade_animal_A3 = {
    "gatekeeper_report": "test_data/clade_animal_A3/speciation_report.json",
    "competitivemapping_report": "test_data/clade_animal_A3/competitivemapping_report.json",
    "mykrobe_report": "test_data/clade_animal_A3/subspecies_report.json",
    "clockwork_report": "test_data/clade_animal_A3/genome_creation_report.json",
    "expected_output": "test_data/clade_animal_A3/main_report.json",
}


@pytest.fixture(
    params=[
        covid,
        SRR2097047,
        NTM,
        WTCHG_885333_73205296_1,
        clade_animal_A3,
    ]
)
def regression_test_set(request) -> dict:
    return request.param


@pytest.fixture
def all_reports_set_individually() -> list:
    return [
        "--gatekeeper",
        "test_data/WTCHG_885333_73205296_1/speciation_report.json",
        "--mapping",
        "test_data/WTCHG_885333_73205296_1/competitivemapping_report.json",
        "--mykrobe",
        "test_data/WTCHG_885333_73205296_1/subspecies_report.json",
        "--clockwork",
        "test_data/WTCHG_885333_73205296_1/genome_creation_report.json",
        "--gnomonicus",
        "test_data/WTCHG_885333_73205296_1/tb/resistance_prediction_report.json",
    ]


@pytest.fixture
def all_reports_set_individually_args(all_reports_set_individually) -> Arguments:
    return Arguments(all_reports_set_individually)


@pytest.fixture
def five_reports() -> list:
    return [
        "--reports",
        "test_data/WTCHG_885333_73205296_1/speciation_report.json",
        "test_data/WTCHG_885333_73205296_1/competitivemapping_report.json",
        "test_data/WTCHG_885333_73205296_1/subspecies_report.json",
        "test_data/WTCHG_885333_73205296_1/genome_creation_report.json",
        "test_data/WTCHG_885333_73205296_1/tb/resistance_prediction_report.json",
    ]


@pytest.fixture
def five_reports_args(five_reports) -> Arguments:
    return Arguments(five_reports)


@pytest.fixture
def three_reports() -> list:
    return [
        "--reports",
        "test_data/WTCHG_885333_73205296_1/speciation_report.json",
        "test_data/WTCHG_885333_73205296_1/competitivemapping_report.json",
        "test_data/WTCHG_885333_73205296_1/subspecies_report.json",
    ]


@pytest.fixture
def three_reports_args(three_reports) -> Arguments:
    return Arguments(three_reports)


@pytest.fixture
def one_report() -> list:
    return [
        "--reports",
        "test_data/WTCHG_885333_73205296_1/speciation_report.json",
    ]


@pytest.fixture
def one_report_args(one_report) -> Arguments:
    return Arguments(one_report)


@pytest.fixture
def bad_report_combination() -> list:
    return [
        "--reports",
        "test_data/WTCHG_885333_73205296_1/speciation_report.json",
        "test_data/WTCHG_885333_73205296_1/tb/resistance_prediction_report.json",
    ]


@pytest.fixture
def no_reports() -> list:
    return ["--reports"]


@pytest.fixture
def bad_reports() -> list:
    return ["--bad", "bad"]


@pytest.fixture
def eg_gatekeeper_report() -> Path:
    return Path("test_data/WTCHG_885333_73205296_1/speciation_report.json")


@pytest.fixture
def eg_gatekeeper_report_contents(eg_gatekeeper_report) -> dict:
    with open(eg_gatekeeper_report, "r") as file:
        return json.load(file)


@pytest.fixture
def eg_competitivemapping_report() -> Path:
    return Path("test_data/WTCHG_885333_73205296_1/competitivemapping_report.json")


@pytest.fixture
def eg_competitivemapping_report_contents(eg_competitivemapping_report) -> dict:
    with open(eg_competitivemapping_report, "r") as file:
        return json.load(file)


@pytest.fixture
def eg_duplicate_tb_competitivemapping_report() -> Path:
    return Path(
        "test_data/WTCHG_885333_73205296_1/duplicate_tb_competitivemapping_report.json"
    )


@pytest.fixture
def eg_duplicate_tb_competitivemapping_report_contents(
    eg_duplicate_tb_competitivemapping_report,
) -> dict:
    with open(eg_duplicate_tb_competitivemapping_report, "r") as file:
        return json.load(file)


@pytest.fixture
def eg_mykrobe_report() -> Path:
    return Path("test_data/WTCHG_885333_73205296_1/subspecies_report.json")


@pytest.fixture
def eg_mykrobe_report_contents(eg_mykrobe_report) -> dict:
    with open(eg_mykrobe_report, "r") as file:
        return json.load(file)


@pytest.fixture
def eg_clockwork_report() -> Path:
    return Path("test_data/WTCHG_885333_73205296_1/genome_creation_report.json")


@pytest.fixture
def eg_clockwork_report_contents(eg_clockwork_report) -> dict:
    with open(eg_clockwork_report, "r") as file:
        return json.load(file)

@pytest.fixture
def eg_gnomonicus_report() -> Path:
    return Path("test_data/WTCHG_885333_73205296_1/tb/resistance_prediction_report.json")


@pytest.fixture
def eg_gnomonicus_report_contents(eg_gnomonicus_report) -> dict:
    with open(eg_gnomonicus_report, "r") as file:
        return json.load(file)
