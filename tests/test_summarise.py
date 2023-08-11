from pathlib import Path

import summary.summarise as summarise


def test_collate_reports(four_reports_args):
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
