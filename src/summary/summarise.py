"""Summay JSON output from GPAS"""

# pylint: disable=logging-not-lazy

import argparse
from enum import Enum
import json
import logging
import os
from pathlib import Path

import pandas as pd

from summary.summarise_gnomonicus import summarise_gnomonicus

REPORT_NAME_MAP = {
    "PIPELINE_BUILD": "versions",
    "knowledge.json": "knowledge",
    "speciation_report.json": "gatekeeper",
    "species_comparison_report.json": "mapping",
    "subspecies_report.json": "mykrobe",
    "genome_creation_report.json": "creation_report",
    "resistance_prediction_report.json": "gnomonicus",
    "name_mapping.csv": "name_mapping",
}


class PipelineOutcome(Enum):
    """Potential outcomes of the pipeline."""

    LOW_MYCO = "Number of Mycobacterial reads is too low to proceed to Mycobacterial species identification."
    LOW_TB = "Mycobacterial species identified. Reads mapped to M. tuberculosis (H37Rv v3) too low to proceed to M. tuberculosis complex genome assembly."
    TB_ASSEMBLED = "Sufficient reads mapped to M. tuberculosis (H37Rv v3) for genome assembly, resistance prediction and relatedness assessment."


logging.basicConfig(
    format="%(asctime)s — %(name)s — %(levelname)s — %(funcName)s:%(lineno)d — %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S%z",
    level=logging.DEBUG,
)
logger = logging.getLogger(__name__)


def read_json_file(path: Path) -> dict:
    """Utility function to load JSON files.

    Args:
        path (Path): Path to JSON file.

    Raises:
        FileNotFoundError: JSON file does not exist.

    Returns:
        dict: JSON file represented as a dictionary.
    """
    if not os.path.isfile(path):
        raise FileNotFoundError(
            "File " + str(path) + " does not exist. Data could not be loaded"
        )
    with open(path, "r", encoding="utf-8") as file:
        data = json.load(file)
    return data


def read_pipeline_build(path: Path) -> str:
    """Read the pipeline build file to find the pipeline build tag

    Args:
        path (Path): Path to the `PIPELINE_BUILD` file

    Returns:
        str: Poller release tag which built this pipeline
    """
    if not os.path.isfile(path):
        raise FileNotFoundError(
            "File " + str(path) + " does not exist. Data could not be loaded"
        )
    with open(path, "r", encoding="utf-8") as file:
        return file.read().strip()


def summarise_gatekeeper(gatekeeper_data: dict) -> dict:
    """Summarises Gatekeeper data.

    Args:
        gatekeeper_data (dict): Output from Gatekeeper

    Returns:
        dict: Summary of organism identification data
    """
    organism = {
        "Human Reads": None,  # comes from CLI data
        "Unclassified Reads": gatekeeper_data.get("unclassified"),
        "Non-Mycobacterium Bacteria Reads": None,
        "Mycobacterium Reads": gatekeeper_data.get("Mycobacteriaceae"),
    }
    logger.warning("Human read data not supported in this version")
    organism["Non-Mycobacterium Bacteria Reads"] = (
        gatekeeper_data["Bacteria"] - organism["Mycobacterium Reads"]
    )
    return organism


def process_lineages(lineages: dict) -> list[dict]:
    """Summarise mykrobe lineages output.

    See https://github.com/Mykrobe-tools/mykrobe/wiki/AMR-prediction-output
    for mykrobe structure

    Args:
        lineages (dict): Just the lineages information from mykrobe

    Returns:
        list[dict]: List of coverage and depth for each lineage detected
    """

    # Note that h37rv is lineage 4.10

    lineage_summary = []

    # For subspecies like Mycobacterium_avium_subsp._silvaticum the structure is simpler
    if "lineage" not in lineages:
        for lineage_name in lineages:
            new_line = {
                "Name": lineage_name,
                "Coverage": lineages[lineage_name]["percent_coverage"],
                "Median Depth": lineages[lineage_name]["median_depth"],
            }
            lineage_summary.append(new_line)
        return lineage_summary

    calls = lineages.get("calls", {})
    for lineage_name in lineages.get("lineage", []):
        new_line = {
            "Name": lineage_name,
            "Coverage": 0,
            "Median Depth": 0,
        }

        if lineage_name not in calls:
            logger.warning(f"Lineage {lineage_name} not found in calls")
            lineage_summary.append(new_line)
            continue

        lineage_call_info = calls.get(lineage_name, {})
        # mykrobe report will have ref-alt data for each lineage determining variant
        # e.g. for both 2, 2.2, and 2.2.5
        # but we only use the most specific so 2.2.5
        call_support = lineage_call_info.get(lineage_name, {})

        # Only expect to find one variant call for a lineage
        variants = list(call_support.keys())
        if len(variants) != 1:
            logger.warning(f"Multiple variant calls found for lineage {lineage_name}")
            lineage_summary.append(new_line)
            continue
        variant_support = call_support.get(variants[0], {})

        genotype = variant_support.get("genotype", [])
        if len(genotype) != 2:
            logger.warning(
                f"Genotype for lineage {lineage_name} not as expected. Should be form [a, b]"
            )
            lineage_summary.append(new_line)
            continue

        called_allele = genotype[0]
        if genotype[0] != genotype[1]:
            # mixed call
            logger.info(
                f"Lineage {lineage_name} has mixed call."
                + " Will report depth/cov for alternate allele."
                + " Unless call is lineage 4 or 4.10 (H37Rv) which uses ref."
            )
            if lineage_name in ["lineage4", "lineage4.10"]:
                called_allele = 0
            else:
                called_allele = 1

        called_allele_name = "reference" if called_allele == 0 else "alternate"
        coverage_info = (
            variant_support.get("info", {})
            .get("coverage", {})
            .get(called_allele_name, {})
        )

        new_line["Coverage"] = coverage_info.get("percent_coverage", 0)
        new_line["Median Depth"] = coverage_info.get("median_depth", 0)
        lineage_summary.append(new_line)

    return lineage_summary


def summarise_mykrobe(mykrobe_data: dict) -> dict:
    """Summarises Mykrobe data.

    Args:
        mykrobe_data (dict): Output from Mykrobe

    Returns:
        dict: Summary of Mykrobe data
    """
    results = {
        "Phylogenic Group": [],
        "Subspecies": [],
        "Lineage": [],
    }

    if mykrobe_data == {}:
        return results

    # Phylo group
    phylo_dict = mykrobe_data.get("phylo_group", {})
    results["Phylogenic Group"] = [
        {
            "Name": group,
            "Coverage": phylo_dict[group].get("percent_coverage"),
            "Median Depth": phylo_dict[group].get("median_depth"),
        }
        for group in phylo_dict
    ]

    # "Subspecies" is called species in mykrobe confusingly
    subspecies_dict = mykrobe_data.get("species", {})
    results["Subspecies"] = [
        {
            "Name": species,
            "Coverage": subspecies_dict[species].get("percent_coverage"),
            "Median Depth": subspecies_dict[species].get("median_depth"),
        }
        for species in subspecies_dict
    ]

    # Lineage (mykrobe)
    if "lineage" in mykrobe_data:
        results["Lineage"] = process_lineages(mykrobe_data.get("lineage", {}))

    return results


def summarise_comp_mapping(
    mapping_data: dict, mykrobe_results: dict, tb_assembled: bool
) -> dict:
    """Summarises Competitive Mapping data.

    Args:
        mapping_data (dict): Output from Competitive Mapping

    Returns:
        dict: Summary of species hits
    """
    mapping_df = pd.DataFrame.from_dict(mapping_data["references"]).sort_values(
        by=["meandepth"], ascending=False
    )

    # depending on competitive mapping the species name will either be in the genome_name column or species column if present
    # For consistency will add species column if not present and populate with genome_name
    if "species" not in mapping_df.columns:
        mapping_df["species"] = mapping_df["genome_name"]

    # For consistency replace "Mycobacterium " with "M." in species column
    mapping_df["species"] = mapping_df["species"].str.replace(
        "Mycobacterium ", "M.", regex=False
    )

    # Want to keep any references which are
    # 1. TB
    # 2. the top hit
    # 3. or has genome coverage over 40%
    # 4. Top NTM hit if mykrobe contains a phylo group other than Mycobacterium_tuberculosis_complex

    winners = mapping_df[
        mapping_df["species"].str.contains("tuberculosis")
        | (mapping_df["coverage"] > 40)
        | (mapping_df["meandepth"] == mapping_df["meandepth"].max())
    ]

    mykrobe_ntm = False
    for phylo_group in mykrobe_results.get("Phylogenic Group", []):
        if phylo_group["Name"] != "Mycobacterium_tuberculosis_complex":
            mykrobe_ntm = True
            break

    if mykrobe_ntm:
        ntm = mapping_df[~mapping_df["species"].str.contains("tuberculosis")]
        # keep first row
        if not ntm.empty:
            winners = pd.concat([winners, ntm.head(1)]).drop_duplicates()

    winners = winners.sort_values(by="meandepth", ascending=False)

    if tb_assembled:
        # If TB is assembled then TB should go first
        winners = pd.concat(
            [
                winners[winners["species"].str.contains("tuberculosis")],
                winners[~winners["species"].str.contains("tuberculosis")],
            ]
        )

    return {
        "Species": [
            {
                "Name": row["species"],
                "Genome": row["genome_name"],
                "Num Reads": int(row["numreads"]),
                "Coverage": row["coverage"],
                "Mean Depth": row["meandepth"],
                "Length": int(row["length"]),
            }
            for _, row in winners.iterrows()
        ]
    }


def summarise_genome_creation(genome_creation_report: dict) -> dict:
    """Summarises sequencing quality"""
    seq_quality = genome_creation_report.get("Sequencing Quality", {})

    if not seq_quality:
        logger.warning("Sequencing Quality not found in genome creation report")
        return {}

    return {
        "Mapped To": "M. tuberculosis (H37Rv v3) NC_000962.3",
        "Coverage": seq_quality["Fixed coverage"],
        "Mixed calls": seq_quality["Mixed calls"],
        "Null calls": seq_quality["Null calls"],
        "Reference genome length": seq_quality["Reference genome length"],
    }


def get_reporting_name(
    cm_name: str,
    name_mapping: pd.DataFrame,
    subspecies: list[str],
    lineages: list[str],
) -> str:
    """Determine the name to report for the organism.

    Args:
        cm_name (str): Name from Competitive Mapping.
        name_mapping (pd.DataFrame): Reference data mapping Competitive Mapping
        and mykrobe outputs to reportable name.
        subspecies (str): All "subspecies" from mykrobe.
        lineages (str): All lineages from mykrobe.

    Returns:
        str: Reportable name for the organism.
    """

    # Check for new lineages e.g. lineage 11.2
    def is_digit_lineage(lineage: str) -> bool:
        return lineage.startswith("lineage") and all(
            char.isdigit() or char == "." for char in lineage[7:]
        )

    if cm_name == "M.tuberculosis":
        new_rows = []
        for lineage in lineages:
            if (
                is_digit_lineage(lineage)
                and lineage not in name_mapping.LINEAGE.unique()
            ):
                # add new lineage to mapping
                new_rows.append(
                    {
                        "reference": "M.tuberculosis",
                        "SPECIES": "Mycobacterium_tuberculosis",
                        "LINEAGE": lineage,
                        "REPORT": f"M. tuberculosis (lineage {lineage[7:]})",
                    }
                )
        if new_rows:
            name_mapping = pd.concat([name_mapping, pd.DataFrame(new_rows)])

    # subset to only the rows that match the competitive mapping name
    name_mapping = name_mapping[name_mapping.reference == cm_name].copy()

    # subset by species
    species_df = name_mapping[name_mapping.SPECIES.isin(subspecies)]
    if species_df.empty:
        # No matches found, fall back to generic case
        species_df = name_mapping[name_mapping.SPECIES == "Unknown"]

    # count number of unique species in table now
    if species_df.SPECIES.nunique() > 1:
        if cm_name == "M.tuberculosis":
            # Special case of mixed species. e.g. canetti and normal tb
            return "MTB Complex (mixed lineage)"
        logger.warning(
            f"More than one unique species {species_df.SPECIES.unique()} found for {cm_name}"
        )
        return f"{cm_name.replace('M.', 'M. ')} (mixed lineage)"

    # subset by lineage
    lineage_df = species_df[species_df.LINEAGE.isin(lineages)]
    if lineage_df.empty:
        # No matches found, fall back to generic case
        lineage_df = species_df[species_df.LINEAGE == "Unknown"]

    if lineage_df.empty:
        # No matches found for cm_name, so return cm_name directly
        return cm_name

    if lineage_df.LINEAGE.nunique() > 1:
        if cm_name == "M.tuberculosis":
            # Specific catches for mixed lineages
            if "africanum" in lineage_df.SPECIES.unique()[0]:
                return "M. africanum (mixed lineage) (MTB complex)"
            if "bovis" in lineage_df.SPECIES.unique()[0]:
                return "M. bovis (mixed lineage) (MTB complex)"
            return "M. tuberculosis (mixed lineage)"

        logger.warning(
            f"More than one unique lineage {lineage_df.LINEAGE.unique()} found for {cm_name}"
        )
        return f"{cm_name.replace('M.', 'M. ')} (mixed lineage)"

    # Can now conclude that there is only one row in the table
    reporting_names = pd.unique(lineage_df.REPORT)
    if len(reporting_names) > 1:
        raise ValueError(
            f"Multiple names: {reporting_names} for {cm_name}. Should not be possible!!"
        )
    return reporting_names[0]


def create_summary(
    reports: dict,
) -> dict:
    """Summarises GPAS pipeline output.

    Args:
        reports (dict): A collection of reports to summarise.

    Returns:
        dict: Summary GPAS pipeline output.
    """

    output = {
        "Pipeline Outcome": PipelineOutcome.LOW_MYCO,
        "Organism Identification": None,
        "Mycobacterium Results": None,
        "Genomes": None,
        "Metadata": {},
    }

    if "versions" in reports:
        pipeline_build = read_pipeline_build(reports["versions"])
        output["Metadata"]["Pipeline build"] = pipeline_build
    if "knowledge" in reports:
        knowledge = read_json_file(reports["knowledge"])
        output["Metadata"]["Reference Data Files"] = knowledge

    if "gatekeeper" in reports:
        output["Organism Identification"] = summarise_gatekeeper(
            read_json_file(reports["gatekeeper"])
        )
    else:
        logger.warning("No gatekeeper report found. Pipeline must have failed.")
        return output

    mykrobe_summary = (
        summarise_mykrobe(read_json_file(reports["mykrobe"]))
        if "mykrobe" in reports
        else {}
    )

    mapping_summary = (
        summarise_comp_mapping(
            read_json_file(reports["mapping"]),
            mykrobe_summary,
            "creation_report" in reports,
        )
        if "mapping" in reports
        else {}
    )

    if "mapping" in reports or "mykrobe" in reports:
        output["Pipeline Outcome"] = PipelineOutcome.LOW_TB
        output["Mycobacterium Results"] = mapping_summary | mykrobe_summary

    # For assemblies currently only support TB
    if "creation_report" in reports:
        output["Pipeline Outcome"] = PipelineOutcome.TB_ASSEMBLED
        assembly_dict = {
            "Name": "M. tuberculosis",
            "Sequencing Quality": summarise_genome_creation(
                read_json_file(reports["creation_report"]),
            ),
        }

        if "gnomonicus" in reports:
            assembly_dict["Resistance Prediction"] = summarise_gnomonicus(
                read_json_file(reports["gnomonicus"])
            )
        output["Genomes"] = [assembly_dict]

    # Now want to make summary section which is a combination of the above
    # Each "species" entry from mapping should get an entry in summary
    if mapping_summary and "name_mapping" in reports:
        name_mapping = pd.read_csv(reports["name_mapping"])
        mykrobe_subspecies = [s["Name"] for s in mykrobe_summary.get("Subspecies", [])]
        mykrobe_lineages = [lin["Name"] for lin in mykrobe_summary.get("Lineage", [])]
        summary = []

        for species_data in mapping_summary["Species"]:
            reporting_name = get_reporting_name(
                species_data["Name"],
                name_mapping,
                mykrobe_subspecies,
                mykrobe_lineages,
            )
            summary.append(
                {
                    "Name": reporting_name,
                    "Num Reads": species_data["Num Reads"],
                    "Coverage": species_data["Coverage"],
                    "Depth": species_data["Mean Depth"],
                    "Length": species_data["Length"],
                }
            )

        output["Mycobacterium Results"] = {
            "Summary": summary,
            **output["Mycobacterium Results"],
        }

    # need to convert pipeline outcome to string for JSON serialisation
    output["Pipeline Outcome"] = output["Pipeline Outcome"].value

    if output["Genomes"]:
        # need to add Num Reads and Mean Depth to Genomes for backwards compatibility
        tb_mapping_data = next(
            sp
            for sp in output["Mycobacterium Results"]["Species"]
            if "tuberculosis" in sp["Name"].lower()
        )
        output["Genomes"][0]["Sequencing Quality"]["Num Reads"] = tb_mapping_data[
            "Num Reads"
        ]
        output["Genomes"][0]["Sequencing Quality"]["Mean Depth"] = tb_mapping_data[
            "Mean Depth"
        ]

    return output


def cli_entry_point() -> None:
    """CLI entry point."""
    reports, output = read_args()
    summary = create_summary(reports)
    with open(output, "w", encoding="utf-8") as file:
        file.write(json.dumps(summary, indent=4))


def report_list_to_dict(report_list: list[str]) -> dict:
    """Convert a list of report files to a dictionary.

    Args:
        report_list (list[str]): List of report files.

    Returns:
        dict: Dictionary of report files.
    """
    reports = {}
    for report in report_list:
        report_name = os.path.basename(report)
        if report_name in REPORT_NAME_MAP:
            reports[REPORT_NAME_MAP[report_name]] = report
        else:
            assigned = False
            for filename, report_type in REPORT_NAME_MAP.items():
                filename_stem = filename.split(".")[0]
                if filename_stem in report_name:
                    reports[report_type] = report
                    assigned = True
                    break

            if not assigned:
                logger.warning(
                    f"Report {report_name} not recognised and will be ignored."
                )
    return reports


def read_args() -> tuple[dict, str]:
    """Use argparse to read reports to dictionary"""
    parser = argparse.ArgumentParser(
        description="Process pipeline output to create a Summary JSON"
    )
    parser.add_argument(
        "--reports",
        nargs="+",
        required=True,
        help="A list of report files, the contents of which will be inferred by filename",
    )
    parser.add_argument(
        "-o",
        "--output",
        default="main_report.json",
        help="Path including name for output json file",
    )
    args = parser.parse_args()
    reports = report_list_to_dict(args.reports)

    return reports, args.output
