from pathlib import Path
import pytest

import summary.summarise as summarise


def test_read_pipeline_build(eg_PIPELINE_BUILD) -> None:
    expected_pipeline_build = "v0.0.55"
    assert expected_pipeline_build == summarise.read_pipeline_build(eg_PIPELINE_BUILD)


def test_generate_sequencing_quality(
    eg_competitivemapping_report_contents, eg_creation_report_contents
) -> None:
    expected_sq_output = {
        "Mapped To": "M.tuberculosis",
        "Num Reads": 3953463.0,
        "Coverage": 98.132,
        "Mean Depth": 132.507,
        "Mixed calls": 351,
        "Null calls": 87041,
        "Reference genome length": 4411532,
    }
    sq_output = summarise.generate_sequencing_quality(
        eg_competitivemapping_report_contents, eg_creation_report_contents
    )
    assert sq_output == expected_sq_output


def test_generate_sequencing_quality_error(
    eg_duplicate_tb_competitivemapping_report_contents, eg_creation_report_contents
) -> None:
    with pytest.raises(ValueError):
        summarise.generate_sequencing_quality(
            eg_duplicate_tb_competitivemapping_report_contents,
            eg_creation_report_contents,
        )


def test_collate_reports_five(five_reports_args):
    expected_reports = {}
    expected_reports["gatekeeper"] = Path(
        "test_data/WTCHG_885333_73205296_1/speciation_report.json"
    )
    expected_reports["mapping"] = Path(
        "test_data/WTCHG_885333_73205296_1/species_comparison_report.json"
    )
    expected_reports["mykrobe"] = Path(
        "test_data/WTCHG_885333_73205296_1/subspecies_report.json"
    )
    expected_reports["creation_report"] = Path(
        "test_data/WTCHG_885333_73205296_1/genome_creation_report.json"
    )
    expected_reports["gnomonicus"] = Path(
        "test_data/WTCHG_885333_73205296_1/tb/resistance_prediction_report.json"
    )
    expected_reports["name_mapping"] = Path("test_data/reference/name_mapping.csv")

    assert expected_reports == summarise.collate_reports(five_reports_args)


def test_collate_reports_three(three_reports_args):
    expected_reports = {}
    expected_reports["gatekeeper"] = Path(
        "test_data/WTCHG_885333_73205296_1/speciation_report.json"
    )
    expected_reports["mapping"] = Path(
        "test_data/WTCHG_885333_73205296_1/species_comparison_report.json"
    )
    expected_reports["mykrobe"] = Path(
        "test_data/WTCHG_885333_73205296_1/subspecies_report.json"
    )
    expected_reports["name_mapping"] = Path("test_data/reference/name_mapping.csv")

    assert expected_reports == summarise.collate_reports(three_reports_args)


def test_collate_reports_one(one_report_args):
    expected_reports = {}
    expected_reports["gatekeeper"] = Path(
        "test_data/WTCHG_885333_73205296_1/speciation_report.json"
    )
    expected_reports["name_mapping"] = Path("test_data/reference/name_mapping.csv")

    assert expected_reports == summarise.collate_reports(one_report_args)


def test_summarise(all_reports_set_individually, tmp_path, mocker):
    args: list = all_reports_set_individually
    args.insert(0, "summary_json")
    tmp_file = tmp_path / "main_report.json"
    args.extend(("--output", str(tmp_file)))

    mocker.patch(
        "sys.argv",
        args,
    )

    summarise.cli_entry_point()

    output = summarise.read_json_file(tmp_file)
    expected_output = summarise.read_json_file(
        "test_data/WTCHG_885333_73205296_1/main_report.json"
    )

    assert output == expected_output
