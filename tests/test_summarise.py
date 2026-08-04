from summary import summarise


def test_read_pipeline_build(eg_PIPELINE_BUILD) -> None:
    expected_pipeline_build = "v0.0.55"
    assert expected_pipeline_build == summarise.read_pipeline_build(eg_PIPELINE_BUILD)
