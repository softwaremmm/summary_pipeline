import json
from pathlib import Path

import pytest

from summary.cli_args import Arguments

covid = {
    "PIPELINE_BUILD": "test_data/covid/PIPELINE_BUILD",
    "gatekeeper_report": "test_data/covid/speciation_report.json",
    "expected_output": "test_data/covid/main_report.json",
    "name_mapping": "test_data/reference/name_mapping.csv",
}

covid_no_meta = {
    "gatekeeper_report": "test_data/covid_no_meta/speciation_report.json",
    "expected_output": "test_data/covid_no_meta/main_report.json",
    "name_mapping": "test_data/reference/name_mapping.csv",
}

SRR2097047 = {
    "PIPELINE_BUILD": "test_data/SRR2097047/PIPELINE_BUILD",
    "gatekeeper_report": "test_data/SRR2097047/speciation_report.json",
    "expected_output": "test_data/SRR2097047/main_report.json",
    "name_mapping": "test_data/reference/name_mapping.csv",
}

MALOMENSE = {
    "gatekeeper_report": "test_data/malmoense_over_40pc/speciation_report.json",
    "competitivemapping_report": "test_data/malmoense_over_40pc/species_comparison_report.json",
    "mykrobe_report": "test_data/malmoense_over_40pc/subspecies_report.json",
    "expected_output": "test_data/malmoense_over_40pc/main_report.json",
    "name_mapping": "test_data/reference/name_mapping.csv",
}

SEPTICUM = {
    "gatekeeper_report": "test_data/septicum/speciation_report.json",
    "competitivemapping_report": "test_data/septicum/species_comparison_report.json",
    "mykrobe_report": "test_data/septicum/subspecies_report.json",
    "expected_output": "test_data/septicum/main_report.json",
    "name_mapping": "test_data/reference/name_mapping.csv",
}

TB_NO_MYKROBE = {
    "gatekeeper_report": "test_data/tb_no_mykrobe/speciation_report.json",
    "competitivemapping_report": "test_data/tb_no_mykrobe/species_comparison_report.json",
    "mykrobe_report": "test_data/tb_no_mykrobe/subspecies_report.json",
    "expected_output": "test_data/tb_no_mykrobe/main_report.json",
    "name_mapping": "test_data/reference/name_mapping.csv",
}

WTCHG_885333_73205296_1 = {
    "PIPELINE_BUILD": "test_data/WTCHG_885333_73205296_1/PIPELINE_BUILD",
    "knowledge": "test_data/WTCHG_885333_73205296_1/knowledge.json",
    "gatekeeper_report": "test_data/WTCHG_885333_73205296_1/speciation_report.json",
    "competitivemapping_report": "test_data/WTCHG_885333_73205296_1/species_comparison_report.json",
    "mykrobe_report": "test_data/WTCHG_885333_73205296_1/subspecies_report.json",
    "creation_report": "test_data/WTCHG_885333_73205296_1/genome_creation_report.json",
    "gnomonicus": "test_data/WTCHG_885333_73205296_1/tb/resistance_prediction_report.json",
    "expected_output": "test_data/WTCHG_885333_73205296_1/main_report.json",
    "name_mapping": "test_data/reference/name_mapping.csv",
}

BCG = {
    "PIPELINE_BUILD": "test_data/BCG/PIPELINE_BUILD",
    "gatekeeper_report": "test_data/BCG/speciation_report.json",
    "competitivemapping_report": "test_data/BCG/species_comparison_report.json",
    "mykrobe_report": "test_data/BCG/subspecies_report.json",
    "creation_report": "test_data/BCG/genome_creation_report.json",
    "gnomonicus": "test_data/BCG/tb/resistance_prediction_report.json",
    "expected_output": "test_data/BCG/main_report.json",
    "name_mapping": "test_data/reference/name_mapping.csv",
}

WTCHG_885333_73205296_2 = {
    "PIPELINE_BUILD": "test_data/WTCHG_885333_73205296_1/PIPELINE_BUILD",
    "gatekeeper_report": "test_data/WTCHG_885333_73205296_1/speciation_report.json",
    "competitivemapping_report": "test_data/WTCHG_885333_73205296_1/species_comparison_report.json",
    "mykrobe_report": "test_data/WTCHG_885333_73205296_1/subspecies_report.json",
    "creation_report": "test_data/WTCHG_885333_73205296_1/genome_creation_report.json",
    "gnomonicus": "test_data/WTCHG_885333_73205296_1/tb/resistance_prediction_report2.json",
    "expected_output": "test_data/WTCHG_885333_73205296_1/main_report2.json",
    "name_mapping": "test_data/reference/name_mapping.csv",
}

WTCHG_885333_73205296_3 = {
    "PIPELINE_BUILD": "test_data/WTCHG_885333_73205296_1/PIPELINE_BUILD",
    "knowledge": "test_data/WTCHG_885333_73205296_1/knowledge.json",
    "gatekeeper_report": "test_data/WTCHG_885333_73205296_1/speciation_report.json",
    "competitivemapping_report": "test_data/WTCHG_885333_73205296_1/species_comparison_report.json",
    "mykrobe_report": "test_data/WTCHG_885333_73205296_1/subspecies_report.json",
    "creation_report": "test_data/WTCHG_885333_73205296_1/genome_creation_report.json",
    "gnomonicus": "test_data/WTCHG_885333_73205296_1/tb/resistance_prediction_report_BDQ.json",
    "expected_output": "test_data/WTCHG_885333_73205296_1/main_report_BDQ.json",
    "name_mapping": "test_data/reference/name_mapping.csv",
}

NO_MYKROBE = {
    "gatekeeper_report": "test_data/no_mykrobe/speciation_report.json",
    "competitivemapping_report": "test_data/no_mykrobe/species_comparison_report.json",
    "mykrobe_report": "test_data/no_mykrobe/subspecies_report.json",
    "expected_output": "test_data/no_mykrobe/main_report.json",
    "name_mapping": "test_data/reference/name_mapping.csv",
}

MIX_NTM_WIN = {
    "gatekeeper_report": "test_data/mix_ntm_win/speciation_report.json",
    "competitivemapping_report": "test_data/mix_ntm_win/species_comparison_report.json",
    "mykrobe_report": "test_data/mix_ntm_win/subspecies_report.json",
    "expected_output": "test_data/mix_ntm_win/main_report.json",
    "name_mapping": "test_data/reference/name_mapping.csv",
}

MIX_TB_WIN = {
    "gatekeeper_report": "test_data/mix_tb_win/speciation_report.json",
    "competitivemapping_report": "test_data/mix_tb_win/species_comparison_report.json",
    "mykrobe_report": "test_data/mix_tb_win/subspecies_report.json",
    "creation_report": "test_data/mix_tb_win/genome_creation_report.json",
    "gnomonicus": "test_data/mix_tb_win/tb/resistance_prediction_report.json",
    "expected_output": "test_data/mix_tb_win/main_report.json",
    "name_mapping": "test_data/reference/name_mapping.csv",
}

NO_LINEAGE_TB = {
    "PIPELINE_BUILD": "test_data/no_lineage_tb/PIPELINE_BUILD",
    "gatekeeper_report": "test_data/no_lineage_tb/speciation_report.json",
    "knowledge": "test_data/no_lineage_tb/knowledge.json",
    "competitivemapping_report": "test_data/no_lineage_tb/species_comparison_report.json",
    "mykrobe_report": "test_data/no_lineage_tb/subspecies_report.json",
    "creation_report": "test_data/no_lineage_tb/genome_creation_report.json",
    "gnomonicus": "test_data/no_lineage_tb/tb/resistance_prediction_report.json",
    "expected_output": "test_data/no_lineage_tb/main_report.json",
    "name_mapping": "test_data/reference/name_mapping.csv",
}

NULL_CALLS_TB = {
    "PIPELINE_BUILD": "test_data/tb_null_calls/PIPELINE_BUILD",
    "gatekeeper_report": "test_data/tb_null_calls/speciation_report.json",
    "knowledge": "test_data/tb_null_calls/knowledge.json",
    "competitivemapping_report": "test_data/tb_null_calls/species_comparison_report.json",
    "mykrobe_report": "test_data/tb_null_calls/subspecies_report.json",
    "creation_report": "test_data/tb_null_calls/genome_creation_report.json",
    "gnomonicus": "test_data/tb_null_calls/resistance_prediction_report.json",
    "expected_output": "test_data/tb_null_calls/main_report.json",
    "name_mapping": "test_data/reference/name_mapping.csv",
}

NO_AA_MUTATIONS_TB = {
    "PIPELINE_BUILD": "test_data/no_lineage_tb/PIPELINE_BUILD",
    "gatekeeper_report": "test_data/no_lineage_tb/speciation_report.json",
    "knowledge": "test_data/no_lineage_tb/knowledge.json",
    "competitivemapping_report": "test_data/no_lineage_tb/species_comparison_report.json",
    "mykrobe_report": "test_data/no_lineage_tb/subspecies_report.json",
    "creation_report": "test_data/no_lineage_tb/genome_creation_report.json",
    "gnomonicus": "test_data/tb_no_aa_mutations/resistance_prediction_report.json",
    "expected_output": "test_data/tb_no_aa_mutations/main_report.json",
    "name_mapping": "test_data/reference/name_mapping.csv",
}

MYKROBE_SPECIES_DIFFERENTIATES = {
    "gatekeeper_report": "test_data/mykrobe_species_differentiates/speciation_report.json",
    "competitivemapping_report": "test_data/mykrobe_species_differentiates/species_comparison_report.json",
    "mykrobe_report": "test_data/mykrobe_species_differentiates/subspecies_report.json",
    "expected_output": "test_data/mykrobe_species_differentiates/main_report.json",
    "name_mapping": "test_data/reference/name_mapping.csv",
}

MIXED_TB_LINEAGE = {
    "gatekeeper_report": "test_data/mixed_tb_lineage/speciation_report.json",
    "competitivemapping_report": "test_data/mixed_tb_lineage/species_comparison_report.json",
    "mykrobe_report": "test_data/mixed_tb_lineage/subspecies_report.json",
    "creation_report": "test_data/mixed_tb_lineage/genome_creation_report.json",
    "gnomonicus": "test_data/mixed_tb_lineage/tb/resistance_prediction_report.json",
    "expected_output": "test_data/mixed_tb_lineage/main_report.json",
    "name_mapping": "test_data/reference/name_mapping.csv",
}

ONT_HET_VARIANT = {
    "gatekeeper_report": "test_data/ont_het_variant/speciation_report.json",
    "competitivemapping_report": "test_data/ont_het_variant/species_comparison_report.json",
    "mykrobe_report": "test_data/ont_het_variant/subspecies_report.json",
    "creation_report": "test_data/ont_het_variant/genome_creation_report.json",
    "gnomonicus": "test_data/ont_het_variant/tb/resistance_prediction_report.json",
    "expected_output": "test_data/ont_het_variant/main_report.json",
    "name_mapping": "test_data/reference/name_mapping.csv",
}

ONT_MANY_HET = {
    "gatekeeper_report": "test_data/ont_many_het/speciation_report.json",
    "competitivemapping_report": "test_data/ont_many_het/species_comparison_report.json",
    "mykrobe_report": "test_data/ont_many_het/subspecies_report.json",
    "creation_report": "test_data/ont_many_het/genome_creation_report.json",
    "gnomonicus": "test_data/ont_many_het/resistance_prediction_report.json",
    "expected_output": "test_data/ont_many_het/main_report.json",
    "name_mapping": "test_data/reference/name_mapping.csv",
}

MORE_CHELONAE_TB_ASSEMBLED = {
    "gatekeeper_report": "test_data/more_chelonae_tb_assembled/speciation_report.json",
    "competitivemapping_report": "test_data/more_chelonae_tb_assembled/species_comparison_report.json",
    "mykrobe_report": "test_data/more_chelonae_tb_assembled/subspecies_report.json",
    "creation_report": "test_data/more_chelonae_tb_assembled/genome_creation_report.json",
    "gnomonicus": "test_data/more_chelonae_tb_assembled/tb/resistance_prediction_report.json",
    "expected_output": "test_data/more_chelonae_tb_assembled/main_report.json",
    "name_mapping": "test_data/reference/name_mapping.csv",
}

AVIUM_SILVATICUM = {
    "gatekeeper_report": "test_data/avium_silvaticum/speciation_report.json",
    "competitivemapping_report": "test_data/avium_silvaticum/species_comparison_report.json",
    "mykrobe_report": "test_data/avium_silvaticum/subspecies_report.json",
    "expected_output": "test_data/avium_silvaticum/main_report.json",
    "name_mapping": "test_data/reference/name_mapping.csv",
}

CANETTII = {
    "gatekeeper_report": "test_data/canettii/speciation_report.json",
    "competitivemapping_report": "test_data/canettii/species_comparison_report.json",
    "mykrobe_report": "test_data/canettii/subspecies_report.json",
    "creation_report": "test_data/canettii/genome_creation_report.json",
    "gnomonicus": "test_data/canettii/tb/resistance_prediction_report.json",
    "expected_output": "test_data/canettii/main_report.json",
    "name_mapping": "test_data/reference/name_mapping.csv",
}

MUNGI = {
    "gatekeeper_report": "test_data/mungi/speciation_report.json",
    "competitivemapping_report": "test_data/mungi/species_comparison_report.json",
    "mykrobe_report": "test_data/mungi/subspecies_report.json",
    "expected_output": "test_data/mungi/main_report.json",
    "name_mapping": "test_data/reference/name_mapping.csv",
}

@pytest.fixture(
    params=[
        covid,
        covid_no_meta,
        SRR2097047,
        TB_NO_MYKROBE,
        SEPTICUM,
        MALOMENSE,
        WTCHG_885333_73205296_1,
        WTCHG_885333_73205296_2,
        WTCHG_885333_73205296_3,
        BCG,
        NO_MYKROBE,
        MIX_NTM_WIN,
        MIX_TB_WIN,
        NO_LINEAGE_TB,
        NULL_CALLS_TB,
        NO_AA_MUTATIONS_TB,
        MYKROBE_SPECIES_DIFFERENTIATES,
        MIXED_TB_LINEAGE,
        ONT_HET_VARIANT,
        ONT_MANY_HET,
        MORE_CHELONAE_TB_ASSEMBLED,
        AVIUM_SILVATICUM,
        CANETTII,
        MUNGI,
    ],
    ids=[
        "covid",
        "covid_no_meta",
        "SRR2097047",
        "TB_NO_MYKROBE",
        "SEPTICUM",
        "MALOMENSE",
        "WTCHG_885333_73205296_1",
        "WTCHG_885333_73205296_2",
        "WTCHG_885333_73205296_3",
        "BCG",
        "NO_MYKROBE",
        "MIX_NTM_WIN",
        "MIX_TB_WIN",
        "NO_LINEAGE_TB",
        "NULL_CALLS_TB",
        "NO_AA_MUTATIONS_TB",
        "mykrobe_species_differentiates",
        "mixed_tb_lineage",
        "ont_het_variant",
        "ont_many_het",
        "more_chelonae_tb_assembled",
        "avium_silvaticum",
        "canettii",
        "mungi",
    ],
)
def regression_test_set(request) -> dict:
    return request.param


@pytest.fixture
def all_reports_set_individually() -> list:
    return [
        "--versions",
        "test_data/WTCHG_885333_73205296_1/PIPELINE_BUILD",
        "--knowledge",
        "test_data/WTCHG_885333_73205296_1/knowledge.json",
        "--gatekeeper",
        "test_data/WTCHG_885333_73205296_1/speciation_report.json",
        "--mapping",
        "test_data/WTCHG_885333_73205296_1/species_comparison_report.json",
        "--mykrobe",
        "test_data/WTCHG_885333_73205296_1/subspecies_report.json",
        "--creation_report",
        "test_data/WTCHG_885333_73205296_1/genome_creation_report.json",
        "--gnomonicus",
        "test_data/WTCHG_885333_73205296_1/tb/resistance_prediction_report.json",
        "--name_mapping",
        "test_data/reference/name_mapping.csv",
    ]


@pytest.fixture
def all_reports_set_individually_args(all_reports_set_individually) -> Arguments:
    return Arguments(all_reports_set_individually)


@pytest.fixture
def all_reports() -> list:
    return [
        "--reports",
        "test_data/WTCHG_885333_73205296_1/PIPELINE_BUILD",
        "test_data/WTCHG_885333_73205296_1/knowledge.json",
        "test_data/WTCHG_885333_73205296_1/speciation_report.json",
        "test_data/WTCHG_885333_73205296_1/species_comparison_report.json",
        "test_data/WTCHG_885333_73205296_1/subspecies_report.json",
        "test_data/WTCHG_885333_73205296_1/genome_creation_report.json",
        "test_data/WTCHG_885333_73205296_1/tb/resistance_prediction_report.json",
        "test_data/reference/name_mapping.csv",
    ]


@pytest.fixture
def all_reports_args(all_reports) -> Arguments:
    return Arguments(all_reports)


@pytest.fixture
def five_reports() -> list:
    return [
        "--reports",
        "test_data/WTCHG_885333_73205296_1/speciation_report.json",
        "test_data/WTCHG_885333_73205296_1/species_comparison_report.json",
        "test_data/WTCHG_885333_73205296_1/subspecies_report.json",
        "test_data/WTCHG_885333_73205296_1/genome_creation_report.json",
        "test_data/WTCHG_885333_73205296_1/tb/resistance_prediction_report.json",
        "test_data/reference/name_mapping.csv",
    ]


@pytest.fixture
def five_reports_args(five_reports) -> Arguments:
    return Arguments(five_reports)


@pytest.fixture
def three_reports() -> list:
    return [
        "--reports",
        "test_data/WTCHG_885333_73205296_1/speciation_report.json",
        "test_data/WTCHG_885333_73205296_1/species_comparison_report.json",
        "test_data/WTCHG_885333_73205296_1/subspecies_report.json",
        "test_data/reference/name_mapping.csv",
    ]


@pytest.fixture
def three_reports_args(three_reports) -> Arguments:
    return Arguments(three_reports)


@pytest.fixture
def one_report() -> list:
    return [
        "--reports",
        "test_data/WTCHG_885333_73205296_1/speciation_report.json",
        "test_data/reference/name_mapping.csv",
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
def bad_path() -> Path:
    return Path("does/not/exist")


@pytest.fixture
def eg_PIPELINE_BUILD() -> Path:
    return Path("test_data/WTCHG_885333_73205296_1/PIPELINE_BUILD")


@pytest.fixture
def eg_gatekeeper_report() -> Path:
    return Path("test_data/WTCHG_885333_73205296_1/speciation_report.json")


@pytest.fixture
def eg_gatekeeper_report_contents(eg_gatekeeper_report) -> dict:
    with open(eg_gatekeeper_report, "r") as file:
        return json.load(file)


@pytest.fixture
def eg_competitivemapping_report() -> Path:
    return Path("test_data/WTCHG_885333_73205296_1/species_comparison_report.json")


@pytest.fixture
def eg_competitivemapping_report_contents(eg_competitivemapping_report) -> dict:
    with open(eg_competitivemapping_report, "r") as file:
        return json.load(file)


@pytest.fixture
def eg_duplicate_tb_competitivemapping_report() -> Path:
    return Path(
        "test_data/WTCHG_885333_73205296_1/duplicate_tb_species_comparison_report.json"
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
def eg_creation_report() -> Path:
    return Path("test_data/WTCHG_885333_73205296_1/genome_creation_report.json")


@pytest.fixture
def eg_creation_report_contents(eg_creation_report) -> dict:
    with open(eg_creation_report, "r") as file:
        return json.load(file)


@pytest.fixture
def eg_gnomonicus_report() -> Path:
    return Path(
        "test_data/WTCHG_885333_73205296_1/tb/resistance_prediction_report.json"
    )


@pytest.fixture
def eg_gnomonicus_report_contents(eg_gnomonicus_report) -> dict:
    with open(eg_gnomonicus_report, "r") as file:
        return json.load(file)
