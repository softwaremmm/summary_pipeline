from pathlib import Path
import pytest
from summary.cli_args import Arguments


def test_Argument_individual_reports(all_reports_set_individually: list):
    cli_args = Arguments(all_reports_set_individually)
    assert cli_args.gatekeeper == Path(
        "test_data/WTCHG_885333_73205296_1/gatekeeper_report.json"
    )
    assert cli_args.mapping == Path(
        "test_data/WTCHG_885333_73205296_1/competitivemapping_report.json"
    )
    assert cli_args.mykrobe == Path(
        "test_data/WTCHG_885333_73205296_1/mykrobe_report.json"
    )
    assert cli_args.gnomonicus == Path(
        "test_data/WTCHG_885333_73205296_1/tb/gnomonicus.json"
    )


def test_Argument_five_reports(five_reports: list):
    cli_args = Arguments(five_reports)
    assert cli_args.gatekeeper == Path(
        "test_data/WTCHG_885333_73205296_1/gatekeeper_report.json"
    )
    assert cli_args.mapping == Path(
        "test_data/WTCHG_885333_73205296_1/competitivemapping_report.json"
    )
    assert cli_args.mykrobe == Path(
        "test_data/WTCHG_885333_73205296_1/mykrobe_report.json"
    )
    assert cli_args.clockwork == Path(
        "test_data/WTCHG_885333_73205296_1/genome_creation_report.json"
    )
    assert cli_args.gnomonicus == Path(
        "test_data/WTCHG_885333_73205296_1/tb/gnomonicus.json"
    )


def test_Argument_three_reports(three_reports: list):
    cli_args = Arguments(three_reports)
    assert cli_args.gatekeeper == Path(
        "test_data/WTCHG_885333_73205296_1/gatekeeper_report.json"
    )
    assert cli_args.mapping == Path(
        "test_data/WTCHG_885333_73205296_1/competitivemapping_report.json"
    )
    assert cli_args.mykrobe == Path(
        "test_data/WTCHG_885333_73205296_1/mykrobe_report.json"
    )
    with pytest.raises(AttributeError):
        cli_args.gnomonicus


def test_Argument_one_report(one_report: list):
    cli_args = Arguments(one_report)
    assert cli_args.gatekeeper == Path(
        "test_data/WTCHG_885333_73205296_1/gatekeeper_report.json"
    )
    with pytest.raises(AttributeError):
        cli_args.mapping
    with pytest.raises(AttributeError):
        cli_args.mykrobe
    with pytest.raises(AttributeError):
        cli_args.gnomonicus
