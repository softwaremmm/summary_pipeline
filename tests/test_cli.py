from pathlib import Path
import pytest
import summary.cli as cli


def test_Argument_individual_reports(all_reports_set_individually: list):
    cli_args = cli.Arguments(all_reports_set_individually)
    assert cli_args.gatekeeper == Path(
        "test_data/example_input/WTCHG_885333_73225298_1/2/gatekeeper_report.json"
    )
    assert cli_args.mapping == Path(
        "test_data/example_input/WTCHG_885333_73225298_1/2/competitivemapping_report.json"
    )
    assert cli_args.mykrobe == Path(
        "test_data/example_input/WTCHG_885333_73225298_1/2/mykrobe_report.json"
    )
    assert cli_args.gnomonicus == Path(
        "test_data/example_input/WTCHG_885333_73225298_1/2/tb/gnomonicus.json"
    )


def test_Argument_four_reports(four_reports: list):
    cli_args = cli.Arguments(four_reports)
    assert cli_args.gatekeeper == Path(
        "test_data/example_input/WTCHG_885333_73225298_1/2/gatekeeper_report.json"
    )
    assert cli_args.mapping == Path(
        "test_data/example_input/WTCHG_885333_73225298_1/2/competitivemapping_report.json"
    )
    assert cli_args.mykrobe == Path(
        "test_data/example_input/WTCHG_885333_73225298_1/2/mykrobe_report.json"
    )
    assert cli_args.gnomonicus == Path(
        "test_data/example_input/WTCHG_885333_73225298_1/2/tb/gnomonicus.json"
    )


def test_Argument_three_reports(three_reports: list):
    cli_args = cli.Arguments(three_reports)
    assert cli_args.gatekeeper == Path(
        "test_data/example_input/WTCHG_885333_73225298_1/2/gatekeeper_report.json"
    )
    assert cli_args.mapping == Path(
        "test_data/example_input/WTCHG_885333_73225298_1/2/competitivemapping_report.json"
    )
    assert cli_args.mykrobe == Path(
        "test_data/example_input/WTCHG_885333_73225298_1/2/mykrobe_report.json"
    )
    with pytest.raises(AttributeError):
        cli_args.gnomonicus


def test_Argument_one_report(one_report: list):
    cli_args = cli.Arguments(one_report)
    assert cli_args.gatekeeper == Path(
        "test_data/example_input/WTCHG_885333_73225298_1/2/gatekeeper_report.json"
    )
    with pytest.raises(AttributeError):
        cli_args.mapping
    with pytest.raises(AttributeError):
        cli_args.mykrobe
    with pytest.raises(AttributeError):
        cli_args.gnomonicus
