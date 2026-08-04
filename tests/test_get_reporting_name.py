import pandas as pd

from summary.summarise import get_reporting_name


def test_get_reporting_name_simple(name_mapping):
    name_mapping = pd.read_csv(name_mapping)
    assert get_reporting_name("M.acidiphilus", name_mapping, [], []) == "M. acidiphilus"
    assert get_reporting_name("M.abscessus", name_mapping, [], []) == "M. abscessus"
    assert (
        get_reporting_name("M.tuberculosis", name_mapping, [], [])
        == "M. tuberculosis (lineage Unknown)"
    )


def test_get_reporting_name_ntm_lineage(name_mapping):
    name_mapping = pd.read_csv(name_mapping)

    assert (
        get_reporting_name(
            "M.abscessus",
            name_mapping,
            ["Mycobacterium_abscessus"],
            ["Mycobacterium_abscessus_subsp._abscessus"],
        )
        == "M. abscessus subsp. abscessus"
    )

    assert (
        get_reporting_name(
            "M.abscessus",
            name_mapping,
            ["Mycobacterium_abscessus", "Irrelevant"],
            ["Mycobacterium_abscessus_subsp._abscessus", "Irrelevant"],
        )
        == "M. abscessus subsp. abscessus"
    )

    assert (
        get_reporting_name(
            "M.abscessus",
            name_mapping,
            ["Mycobacterium_abscessus"],
            [
                "Mycobacterium_abscessus_subsp._abscessus",
                "Mycobacterium_abscessus_subsp._bolletii",
            ],
        )
        == "M. abscessus (mixed lineage)"
    )

    assert (
        get_reporting_name(
            "M.heraklionensis",
            name_mapping,
            ["Mycobacterium_heraklionense_A", "Mycobacterium_heraklionense_B"],
            [],
        )
        == "M. heraklionensis (mixed lineage)"
    )


def test_get_reporting_name_tb(name_mapping):
    name_mapping = pd.read_csv(name_mapping)

    assert (
        get_reporting_name(
            "M.tuberculosis",
            name_mapping,
            ["Mycobacterium_tuberculosis"],
            ["lineage1.1"],
        )
        == "M. tuberculosis (lineage 1.1)"
    )

    assert (
        get_reporting_name(
            "M.tuberculosis",
            name_mapping,
            ["Mycobacterium_tuberculosis"],
            ["lineage1.1", "other"],
        )
        == "M. tuberculosis (lineage 1.1)"
    )

    assert (
        get_reporting_name(
            "M.tuberculosis",
            name_mapping,
            ["Mycobacterium_tuberculosis"],
            ["lineage1.1", "lineage7"],
        )
        == "M. tuberculosis (mixed lineage)"
    )

    assert (
        get_reporting_name(
            "M.tuberculosis",
            name_mapping,
            ["Mycobacterium_tuberculosis_variant_africanum"],
            ["lineage6"],
        )
        == "M. africanum (lineage 6) (MTB complex)"
    )

    assert (
        get_reporting_name(
            "M.tuberculosis",
            name_mapping,
            ["Mycobacterium_tuberculosis_variant_africanum"],
            ["lineage6", "lineage5"],
        )
        == "M. africanum (mixed lineage) (MTB complex)"
    )

    assert (
        get_reporting_name(
            "M.tuberculosis",
            name_mapping,
            ["Mycobacterium_tuberculosis", "other"],
            ["lineage5"],
        )
        == "M. tuberculosis (lineage 5)"
    )

    assert (
        get_reporting_name(
            "M.tuberculosis",
            name_mapping,
            [
                "Mycobacterium_tuberculosis",
                "Mycobacterium_tuberculosis_variant_microti",
            ],
            ["lineage5"],
        )
        == "MTB Complex (mixed lineage)"
    )

    assert (
        get_reporting_name(
            "M.tuberculosis",
            name_mapping,
            [
                "Mycobacterium_bovis",
            ],
            ["lineageBovis", "lineageBovis.BCG"],
        )
        == "M. bovis (mixed lineage) (MTB complex)"
    )
