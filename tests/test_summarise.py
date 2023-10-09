from pathlib import Path
import pytest

import summary.summarise as summarise


def test_read_pipeline_versions_file(eg_pipeline_versions) -> None:
    expected_output = {
        "human-read-removal_pipeline": "v0.1.4",
        "gatekeeper_pipeline": "v0.1.9",
        "lineagecalling_pipeline": "v0.1.5",
        "competitivemapping_pipeline": "v0.1.8",
        "clockwork_pipeline": "v0.2.2",
        "tb-predict-pipeline": "v0.3.0",
        "fn5_pipeline": "v1.0.3",
        "summary_pipeline": "1.1.7",
        "gpas-tb-workflow": "v0.0.55",
    }
    pipeline_versions_output = summarise.read_pipeline_versions_file(
        eg_pipeline_versions
    )
    assert pipeline_versions_output == expected_output


def test_read_pipeline_versions_file_error(bad_path) -> None:
    with pytest.raises(FileNotFoundError):
        summarise.read_pipeline_versions_file(bad_path)


def test_generate_sequencing_quality(
    eg_competitivemapping_report_contents, eg_clockwork_report_contents
) -> None:
    expected_sq_output = {
        "Mapped To": "Mycobacterium tuberculosis H37Rv complete genome",
        "Num Reads": 3953463.0,
        "Coverage": 98.132,
        "Mean Depth": 132.507,
        "Mixed calls": 351,
    }
    sq_output = summarise.generate_sequencing_quality(
        eg_competitivemapping_report_contents, eg_clockwork_report_contents
    )
    assert sq_output == expected_sq_output


def test_generate_sequencing_quality_error(
    eg_duplicate_tb_competitivemapping_report_contents, eg_clockwork_report_contents
) -> None:
    with pytest.raises(ValueError):
        summarise.generate_sequencing_quality(
            eg_duplicate_tb_competitivemapping_report_contents,
            eg_clockwork_report_contents,
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
    expected_reports["clockwork"] = Path(
        "test_data/WTCHG_885333_73205296_1/genome_creation_report.json"
    )
    expected_reports["gnomonicus"] = Path(
        "test_data/WTCHG_885333_73205296_1/tb/resistance_prediction_report.json"
    )

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

    assert expected_reports == summarise.collate_reports(three_reports_args)


def test_collate_reports_one(one_report_args):
    expected_reports = {}
    expected_reports["gatekeeper"] = Path(
        "test_data/WTCHG_885333_73205296_1/speciation_report.json"
    )

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
