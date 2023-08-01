import pytest
from pathlib import Path

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


@pytest.fixture(params=[WTCHG_885333_73225298_1_1, WTCHG_885333_73225298_1_2])
def test_set(request) -> dict:
    return request.param
