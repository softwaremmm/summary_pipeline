from pathlib import Path

import summary.summarise as summarise


def test_collate_reports_four(four_reports_args):
    expected_reports = {}
    expected_reports["gatekeeper"] = Path(
        "test_data/WTCHG_885333_73205296_1/gatekeeper_report.json"
    )
    expected_reports["mapping"] = Path(
        "test_data/WTCHG_885333_73205296_1/competitivemapping_report.json"
    )
    expected_reports["mykrobe"] = Path(
        "test_data/WTCHG_885333_73205296_1/mykrobe_report.json"
    )
    expected_reports["gnomonicus"] = Path(
        "test_data/WTCHG_885333_73205296_1/tb/gnomonicus.json"
    )

    assert expected_reports == summarise.collate_reports(four_reports_args)


def test_collate_reports_three(three_reports_args):
    expected_reports = {}
    expected_reports["gatekeeper"] = Path(
        "test_data/WTCHG_885333_73205296_1/gatekeeper_report.json"
    )
    expected_reports["mapping"] = Path(
        "test_data/WTCHG_885333_73205296_1/competitivemapping_report.json"
    )
    expected_reports["mykrobe"] = Path(
        "test_data/WTCHG_885333_73205296_1/mykrobe_report.json"
    )

    assert expected_reports == summarise.collate_reports(three_reports_args)


def test_collate_reports_one(one_report_args):
    expected_reports = {}
    expected_reports["gatekeeper"] = Path(
        "test_data/WTCHG_885333_73205296_1/gatekeeper_report.json"
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
