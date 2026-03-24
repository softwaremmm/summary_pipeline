"""Summay JSON output from GPAS"""

# pylint: disable=logging-not-lazy

import json
import logging
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from summary.cli_args import Arguments

logging.basicConfig(
    format="%(asctime)s — %(name)s — %(levelname)s — %(funcName)s:%(lineno)d — %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S%z",
    level=logging.DEBUG,
)

treatment_classes = {
    "First-line treatment": ["INH", "RIF", "PZA", "EMB"],
    "Second-line treatment": ["MXF", "LEV", "LZD", "BDQ"],
    "Reserve treatment": ["AMI", "KAN", "STM", "CAP", "ETH", "DLM", "CFZ"],
}

drug_names = {
    "AMC": "Amoxicilin-Clavulanate",
    "AMI": "Amikacin",
    "AMX": "Amoxicilin",
    "AZM": "Azithromycin",
    "BDQ": "Bedaquiline",
    "CAP": "Capreomycin",
    "CFZ": "Clofazimine",
    "CIP": "Ciprofloxacin",
    "CLR": "Clarithromycin",
    "CYC": "Cycloserine",
    "DCS": "D-Cycloserine",
    "DLM": "Delamanid",
    "EMB": "Ethambutol",
    "ETH": "Ethionamide",
    "ETP": "Ertapenem",
    "FQS": "Fluoroquinolone",
    "GEN": "Gentamicin",
    "GFX": "Gatifloxacin",
    "IMI": "Imipenem",
    "INH": "Isoniazid",
    "KAN": "Kanamycin",
    "LEV": "Levofloxacin",
    "LZD": "Linezolid",
    "MEF": "Mefloquine",
    "MPM": "Meropenem",
    "MXF": "Moxifloxacin",
    "OFX": "Ofloxacin",
    "PAN": "Pretomanid",
    "PAS": "Pas",
    "PTO": "Prothionamide",
    "PZA": "Pyrazinamide",
    "RFB": "Rifabutin",
    "RIF": "Rifampicin",
    "STM": "Streptomycin",
    "STX": "Sitafloxacin",
    "SXT": "Cotrimoxazole",
    "SZD": "Sutezolid",
    "TRD": "Terizidone",
    "TZE": "Thioacetazone",
}


def generate_organism_identification(gatekeeper_data: dict) -> dict:
    """Summarises organism identification data.

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
    logging.warning("Human read data not supported in this version")
    organism["Non-Mycobacterium Bacteria Reads"] = (
        gatekeeper_data["Bacteria"] - organism["Mycobacterium Reads"]
    )
    return organism


def generate_mycobacterium_results(
    mappings: dict,
    mykrobe_data: dict,
    name_mapping: pd.DataFrame,
    tb_genome_assembled: bool = False,
    tb_reference_name: str = "M.tuberculosis",
) -> dict:
    """Summarises Competitive Mapping and Mykrobe outputs.

    Args:
        mappings (dict): Output from Competitive Mapping.
        mykrobe_data (dict): Output from Mykrobe.
        name_mapping (pd.DataFrame): Mapping of reference names and mykrobe "lineages" to reportable names.
        tb_genome_assembled (bool, optional): True if M. tuberculosis genome was assembled. Defaults to False.
        tb_reference_name (str, optional): Name of M. tuberculosis reference. Defaults to "M.tuberculosis".

    Returns:
        dict: Summary of Competitive Mapping and Mykrobe outputs.
    """
    myco: dict[str, list] = {
        "Summary": [],
        "Species": [],
        "Phylogenic Group": [],
        "Subspecies": [],
        "Lineage": [],
    }

    # Add mykrobe data for phylo group, subspecies, and lineage
    mixed_phylo_pop = False
    if mykrobe_data != {}:
        # Phylogenetic Group (mykrobe)
        myco["Phylogenic Group"] = process_phylo_group(
            mykrobe_data.get("phylo_group", {})
        )

        # "Subspecies" (mykrobe)
        if "species" in mykrobe_data:
            myco["Subspecies"] = process_subspecies(
                mykrobe_data.get("species", {})
            )  # Why is species assigned to subspecies? Because these ideas are conflated in TB complex.

        # Lineage (mykrobe)
        if "lineage" in mykrobe_data:
            myco["Lineage"] = process_lineages(mykrobe_data.get("lineage", {}))

        if len(myco["Phylogenic Group"]) == 2:
            mixed_phylo_pop = True
        elif len(myco["Phylogenic Group"]) > 2:
            raise ValueError("Mixed population with more than two phylo groups.")
    lineages = [lin["Name"] for lin in myco["Lineage"]]
    subspecies = [sub["Name"] for sub in myco["Subspecies"]]

    # Which hits to report?
    # Should report TB first if TB genome assembled
    # Should always report TB if present
    # Should report non-TB species if mixed phylogenetic population

    mappings_sorted = pd.DataFrame.from_dict(mappings["references"]).sort_values(
        by=["meandepth"], ascending=False
    )
    tophit = mappings_sorted.head(1).to_dict(orient="records")[0]
    hits = [tophit]

    # if tb present always include it
    if tophit["genome_name"] != tb_reference_name:
        tb_row = mappings_sorted[mappings_sorted["genome_name"] == tb_reference_name]
        if not tb_row.empty:
            tb_hit = tb_row.to_dict(orient="records")[0]
            if tb_genome_assembled:
                hits.insert(0, tb_hit)
            else:
                hits.append(tb_hit)

    # if mixed phylo population, make sure top non-tb hit is included
    if tophit["genome_name"] == tb_reference_name and mixed_phylo_pop:
        second_hit = mappings_sorted.head(2).to_dict(orient="records")[1]
        hits.append(second_hit)

    # Species comes directly from competitive mapping
    myco["Species"] = [
        {
            "Name": hit["genome_name"],
            "Num Reads": int(hit["numreads"]),
            "Coverage": hit["coverage"],
            "Mean Depth": hit["meandepth"],
            "Length": hit["length"],
        }
        for hit in hits
    ]

    # Summary is just species with the reportable name
    myco["Summary"] = [
        {
            "Name": organism_name(
                hit["genome_name"],
                name_mapping,
                subspecies,
                lineages,
            ),
            "Num Reads": int(hit["numreads"]),
            "Coverage": hit["coverage"],
            "Depth": hit["meandepth"],
        }
        for hit in hits
    ]

    return myco


def generate_assembled_results(
    mappings: dict,
    mykrobe_data: dict,
    name_mapping: pd.DataFrame,
    assembled_species: list[str],
) -> dict:
    """Summarises Competitive Mapping and Mykrobe outputs.

    Args:
        mappings (dict): Output from Competitive Mapping.
        mykrobe_data (dict): Output from Mykrobe.
        name_mapping (pd.DataFrame): Mapping of reference names and mykrobe "lineages" to reportable names.
        assembled_species (list[str]): List of the species with assembled genomes.

    Returns:
        dict: Summary of Competitive Mapping and Mykrobe outputs.
    """
    myco: dict[str, list] = {
        "Summary": [],
        "Species": [],
        "Phylogenic Group": [],
        "Subspecies": [],
        "Lineage": [],
    }
    if len(assembled_species) == 0:
        return myco

    # Add mykrobe data for phylo group, subspecies, and lineage
    if mykrobe_data != {}:
        # Phylogenetic Group (mykrobe)
        myco["Phylogenic Group"] = process_phylo_group(
            mykrobe_data.get("phylo_group", {})
        )

        # "Subspecies" (mykrobe)
        if "species" in mykrobe_data:
            myco["Subspecies"] = process_subspecies(
                mykrobe_data.get("species", {})
            )  # Why is species assigned to subspecies? Because these ideas are conflated in TB complex.

        # Lineage (mykrobe)
        if "lineage" in mykrobe_data:
            myco["Lineage"] = process_lineages(mykrobe_data.get("lineage", {}))

    lineages = [lin["Name"] for lin in myco["Lineage"]]
    subspecies = [sub["Name"] for sub in myco["Subspecies"]]

    # Which hits to report?
    # Should report TB first if TB genome assembled
    # Should always report TB if present
    # Should report non-TB species if mixed phylogenetic population

    mappings_sorted = pd.DataFrame.from_dict(mappings["references"]).sort_values(
        by=["meandepth"], ascending=False
    )

    # Pull out the hits based on non-case-sensitive match to the assembled species
    # Much easier to do this than guarantee all cases match
    assembled_species = {sp.lower() for sp in assembled_species}
    hits = [
        hit
        for hit in mappings_sorted.head(1).to_dict(orient="records")
        if hit["genome_name"].lower() in assembled_species
    ]

    # Species comes directly from competitive mapping
    myco["Species"] = [
        {
            "Name": hit["genome_name"],
            "Num Reads": int(hit["numreads"]),
            "Coverage": hit["coverage"],
            "Mean Depth": hit["meandepth"],
            "Length": hit["length"],
        }
        for hit in hits
    ]

    # Summary is just species with the reportable name
    myco["Summary"] = [
        {
            "Name": organism_name(
                hit["genome_name"],
                name_mapping,
                subspecies,
                lineages,
            ),
            "Num Reads": int(hit["numreads"]),
            "Coverage": hit["coverage"],
            "Depth": hit["meandepth"],
        }
        for hit in hits
    ]

    return myco


def process_phylo_group(phylo_group: dict) -> list[dict]:
    """Restructure phylogenetic group information from mykrobe

    Args:
        phylo_group (dict): Phylogenetic group information from mykrobe

    Raises:
        ValueError: Thrown if multiple phyogenetic groups are found

    Returns:
        list[dict]: Restructured phylogenetic information
    """
    phylos = []
    for group in phylo_group:
        phylo = {
            "Name": group,
            "Coverage": phylo_group[group].get("percent_coverage"),
            "Median Depth": phylo_group[group].get("median_depth"),
        }
        phylos.append(phylo)

    return phylos


def process_subspecies(species: dict) -> list[dict]:
    """Restructure species information from mykrobe

    Args:
        species (dict): Species information from mykrobe

    Raises:
        ValueError: Throws an error if mykrobe returns more than one species

    Returns:
        list[dict]: Restructured species information
    """

    subspecies = []
    for specie in species:
        specie = {
            "Name": specie,
            "Coverage": species[specie].get("percent_coverage"),
            "Median Depth": species[specie].get("median_depth"),
        }
        subspecies.append(specie)

    return subspecies


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
            logging.warning(f"Lineage {lineage_name} not found in calls")
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
            logging.warning(f"Multiple variant calls found for lineage {lineage_name}")
            lineage_summary.append(new_line)
            continue
        variant_support = call_support.get(variants[0], {})

        genotype = variant_support.get("genotype", [])
        if len(genotype) != 2:
            logging.warning(
                f"Genotype for lineage {lineage_name} not as expected. Should be form [a, b]"
            )
            lineage_summary.append(new_line)
            continue

        called_allele = genotype[0]
        if genotype[0] != genotype[1]:
            # mixed call
            logging.info(
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


def organism_name(
    cm_name: str,
    mapping: pd.DataFrame,
    species: list[str],
    lineages: list[str],
) -> str:
    """Determine the name to report for the organism.

    Args:
        cm_name (str): Name from Competitive Mapping.
        mapping (pd.DataFrame): Reference data mapping Competitive Mapping
        and mykrobe outputs to reportable name.
        species (str): All species from mykrobe.
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
            if is_digit_lineage(lineage) and lineage not in mapping.LINEAGE.unique():
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
            mapping = pd.concat([mapping, pd.DataFrame(new_rows)])

    # subset to only the rows that match the competitive mapping name
    mapping = mapping[mapping.reference == cm_name].copy()

    # subset by species
    species_df = mapping[mapping.SPECIES.isin(species)]
    if species_df.empty:
        # No matches found, fall back to generic case
        species_df = mapping[mapping.SPECIES == "Unknown"]

    # count number of unique species in table now
    if species_df.SPECIES.nunique() > 1:
        if cm_name == "M.tuberculosis":
            # Special case of mixed species. e.g. canetti and normal tb
            return "MTB Complex (mixed lineage)"
        logging.warning(
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

        logging.warning(
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


def generate_sequencing_quality(mappings: dict, genome_creation_report: dict) -> dict:
    """Summarises sequencing quality.

    Args:
        mappings (dict): Competitive Mapping output.

    Returns:
        dict: Summary of sequencing quality.
    """
    # Much of this data is a repeat of data already in Myco Results
    tb_mappings = list(
        filter(
            lambda mapping: "tuberculosis" in mapping["genome_name"],
            mappings["references"],
        )
    )
    if len(tb_mappings) > 1:
        raise ValueError(
            "More than one mapping to M.tuberculosis. Possible manifest problem."
        )
    tb_mapping = tb_mappings[0]

    genome_name = tb_mapping["genome_name"]

    match genome_name:
        case "M.tuberculosis":
            mapped_to_name = "M. tuberculosis (H37Rv v3) NC_000962.3"
        case _:
            mapped_to_name = genome_name

    seq_qual = {
        "Mapped To": mapped_to_name,
        "Num Reads": tb_mapping["numreads"],
        "Coverage": genome_creation_report["Sequencing Quality"]["Fixed coverage"],
        "Mean Depth": tb_mapping["meandepth"],
        "Mixed calls": genome_creation_report["Sequencing Quality"]["Mixed calls"],
        "Null calls": genome_creation_report["Sequencing Quality"]["Null calls"],
        "Reference genome length": genome_creation_report["Sequencing Quality"][
            "Reference genome length"
        ],
    }

    return seq_qual


def construct_payload(significant_variants_df: pd.DataFrame) -> list:
    """Construct Resistance Prediction Details payload for the summary JSON.

    Args:
        significant_variants_df (pd.DataFrame):

    Returns:
        list: results for incorporation in summary JSON
    """

    drugs = []
    payload = []
    valid_nucleotides = ["a", "t", "c", "g", "x", "z"]

    # TODO: tried to do more elegantly with pd.to_json() but ended up doing simply

    # create an alphabetical list of the drugs
    drugs = significant_variants_df.drug.unique()
    drugs = sorted(drugs)

    drug_blocks = {}
    for drug in drugs:
        drug_blocks[drug] = {"Drug Name": drug, "Mutations": []}

    seen_mutations = {}

    for idx, row in significant_variants_df.iterrows():
        significant_variant = {}
        keep = True

        if pd.isnull(row.gene):
            significant_variant["Gene"] = None
        else:
            significant_variant["Gene"] = row.gene

        significant_variant["Mutation"] = row.mutation

        if pd.isnull(row.gene_position):
            significant_variant["Position"] = None
        else:
            significant_variant["Position"] = int(row.gene_position)

        if isinstance(row.ref, str):
            significant_variant["Ref"] = row.ref
        elif (
            row.mutation[0] in valid_nucleotides
            and row.mutation[-1] in valid_nucleotides
        ):
            significant_variant["Ref"] = row.mutation[0]
        else:
            significant_variant["Ref"] = ""
        if isinstance(row.alt, str):
            significant_variant["Alt"] = row.alt
        elif (
            row.mutation[0] in valid_nucleotides
            and row.mutation[-1] in valid_nucleotides
        ):
            significant_variant["Alt"] = row.mutation[-1]
        else:
            significant_variant["Alt"] = ""
        if row.coverage_ref == "Complex" and row.coverage_alt == "Complex":
            significant_variant["Coverage"] = ["Complex", "Complex"]
        else:
            significant_variant["Coverage"] = [
                int(row.coverage_ref)
                if row.coverage_ref is not None and row.coverage_ref >= 0
                else None,
                int(row.coverage_alt)
                if row.coverage_alt is not None and row.coverage_alt >= 0
                else None,
            ]

        if seen_mutations.get(
            (row.drug, significant_variant["Gene"], significant_variant["Mutation"])
        ):
            # Already seen this mutation so check if this is variant's coverage is less
            old_idx, significant_cov = seen_mutations.get(
                (row.drug, significant_variant["Gene"], significant_variant["Mutation"])
            )
            if significant_cov[0] is not None and significant_cov[0] != "Complex":
                if significant_variant["Coverage"][0] is not None:
                    if significant_variant["Coverage"][0] > significant_cov[0]:
                        keep = False
                else:
                    # Last row for this codon gave a specific value, this didn't, so don't keep this
                    keep = False
            if significant_cov[1] is not None and significant_cov[1] != "Complex":
                if significant_variant["Coverage"][1] is not None:
                    if significant_variant["Coverage"][1] > significant_cov[1]:
                        keep = False
                else:
                    # Last row for this codon gave a specific value, this didn't, so don't keep this
                    keep = False

            if keep:
                # Remove the old one in favour of this
                del drug_blocks[row.drug]["Mutations"][old_idx]

        significant_variant["Prediction"] = row.prediction
        if row.evidence == {}:
            significant_variant["Evidence"] = ""
        else:
            significant_variant["Evidence"] = row.evidence

        drug_blocks[row.drug]["Mutations"].append(significant_variant)
        seen_mutations[
            (row.drug, significant_variant["Gene"], significant_variant["Mutation"])
        ] = (
            len(drug_blocks[row.drug]["Mutations"]) - 1,
            significant_variant["Coverage"],
        )

    for drug_name in drugs:
        payload.append(drug_blocks[drug_name])

    return payload


def unpack_COV_from_info(row: pd.Series) -> pd.Series:
    """Helper pd function for retrieving the COV from the INFO column

    Args:
        row (pd.Series): row passed from pd apply function

    Returns:
        pd.Series: REF and ALT coverage values
    """
    result = pd.Series([np.float64("nan"), np.float64("nan")])
    if row.vcf_idx is not None and row.vcf_idx >= 0:
        idx = int(row.vcf_idx)
        if "COV" in row.vcf_evidence:
            if len(row.vcf_evidence["COV"]) == 1:
                # Edge case of only one COV value
                if idx == 0:
                    # It's a ref (probably a null) so put in just the ref coverage
                    result = pd.Series([row.vcf_evidence["COV"][0], 0])
                else:
                    # It's an alt (probably a null) so put in just the alt coverage
                    result = pd.Series([0, row.vcf_evidence["COV"][idx]])
            else:
                if idx == 0:
                    # It's a ref (probably a null) so put in the ref coverage
                    result = pd.Series([row.vcf_evidence["COV"][0], 0])
                else:
                    # It's not a ref call, so give ref and alt coverage
                    result = pd.Series(
                        [row.vcf_evidence["COV"][0], row.vcf_evidence["COV"][idx]]
                    )
        elif "VCF row is complex" in row.vcf_evidence:
            # Complex row, so despite no VCF evidence, we want to mark as such
            result = pd.Series(["Complex", "Complex"])
    return result


def generate_resistance_prediction(gnomonicus_data: dict) -> dict:
    """Summarises resistance prediction information,

    Args:
        gnomonicus_data (dict): Gnomonicus output.

    Raises:
        ValueError: Unknown mutation.
        ValueError: Unknown gene position.
        ValueError: Unknown gene.

    Returns:
        dict: Summary of resistance prediction information.
    """
    amr = {"Resistance Prediction Summary": {}, "Resistance Prediction Detail": []}
    data = gnomonicus_data.get("data")
    meta = gnomonicus_data.get("meta")

    # There's 2 main situations here:
    # 1. Populated everything - a sample had >=1 variant within a resistance gene
    # 2. Limited fields populated - a sample had 0 variants within resistance genes
    # In both, the antibiogram is populated

    # let's put the drugs in alphabetical order
    raw_antibiogram = dict(sorted((data.get("antibiogram")).items()))
    if meta.get("catalogue_name") != "WHO-UCN-GTB-PCI-2023.5":
        # Filter out BDQ if we haven't used WHO v2
        raw_antibiogram["BDQ"] = "-"
    antibiogram = {}
    # the code below groups the drugs according to the treatment_classes
    # this effectively hardcodes version 1 of the WHO catalogue
    # -> will need generalising if we are to use multiple catalogues
    for treatment_category, drug_list in treatment_classes.items():
        antibiogram[treatment_category] = {}
        # drug3 is the 3 letter code
        for drug3 in drug_list:
            drug_name_long = drug_names[drug3] + " (" + drug3 + ")"
            antibiogram[treatment_category][drug_name_long] = raw_antibiogram.get(
                drug3, "-"
            )

    amr["Resistance Prediction Summary"] = antibiogram

    # Check if we have situtation 1 or 2
    if len(data.get("effects")) == 0:
        # Situation 2 - no variants
        amr["Resistance Prediction Detail"] = []
    else:
        # Situation 1 - variants

        # retrieve the effects block and build our base pd DataFrame
        effects = data.get("effects")
        effects_list = []
        for drug_name in effects:
            for effect_mutation in effects[drug_name]:
                if "phenotype" not in effect_mutation:
                    effect_mutation["drug"] = drug_name
                    effects_list.append(effect_mutation)
        effects_df = pd.DataFrame(effects_list)
        effects_df.set_index(["gene", "mutation"], inplace=True)

        # retrieve the mutations block and build another pd DataFrame
        mutations_list = data.get("mutations")
        mutations_df = pd.DataFrame(mutations_list)
        # In cases of 0 AA mutations, no `ref` or `alt` fields are present
        # so put in dummy values for these
        if "ref" not in mutations_df.columns:
            mutations_df["ref"] = np.nan
        if "alt" not in mutations_df.columns:
            mutations_df["alt"] = np.nan
        mutations_df.set_index(["gene", "mutation"], inplace=True)

        # now left-join mutations to effects so we can get the a few extra columns
        # note that this can be many:1 since a single mutation can affect multiple drugs
        effects_muts_df = effects_df.join(mutations_df[["ref", "alt", "gene_position"]])
        effects_muts_df.reset_index(inplace=True)
        effects_muts_df.set_index(["gene", "gene_position"], inplace=True)

        # finally, retrieve the variants block and build the final DataFrame
        variants = data.get("variants")
        variants_df = pd.DataFrame(variants)
        variants_df.rename(columns={"gene_name": "gene"}, inplace=True)
        variants_df.set_index(["gene", "gene_position"], inplace=True)

        # now left-join to variants so we can get at the INFO field held
        #  in vcf_evidence as this contains COV
        # note this can be 1:many since a single mutation can be made up
        #  of multiple variants (e.g. multiple SNPs, minor alleles etc)
        effects_muts_vars_df = effects_muts_df.join(
            variants_df[["vcf_evidence", "vcf_idx"]]
        )
        effects_muts_vars_df.reset_index(inplace=True)
        effects_muts_vars_df.set_index(["drug", "gene", "mutation"], inplace=True)

        # use the pd helper function defined elsewhere to extract COV from the vcf_evidence field
        effects_muts_vars_df[["coverage_ref", "coverage_alt"]] = (
            effects_muts_vars_df.apply(unpack_COV_from_info, axis=1)
        )
        effects_muts_vars_df.drop(columns=["vcf_evidence", "vcf_idx"], inplace=True)

        # ignore mutations that have no effect
        # now we have a DataFrame with all the fields and so can construct the dict payload
        effects_muts_vars_df.reset_index(inplace=True)
        effects_muts_vars_df = effects_muts_vars_df[
            (effects_muts_vars_df["mutation"].str.contains(r"&"))
            | (effects_muts_vars_df.prediction != "S")
        ]

        payload = construct_payload(effects_muts_vars_df)
        amr["Resistance Prediction Detail"] = payload

    return amr


def create_summary(
    reports: dict,
    assembled_species: list[str] = [],
) -> dict:
    """Summarises GPAS pipeline output.

    Args:
        reports (dict): A collection of reports to summarise.
        assembled_species (list[str], optional): List of species with assembled genomes. Defaults to [].

    Returns:
        dict: Summary GPAS pipeline output.
    """

    output = {}
    if "gatekeeper" in reports:
        output["Pipeline Outcome"] = (
            "Number of Mycobacterial reads is too low to proceed to Mycobacterial species identification."
        )
        gatekeeper_json = read_json_file(reports["gatekeeper"])
        output["Organism Identification"] = generate_organism_identification(
            gatekeeper_json
        )
    else:
        output = "Pipeline failed to produce a summary (summary_pipeline could not find gatekeeper report)."
    if "mapping" in reports and "mykrobe" in reports:
        output["Pipeline Outcome"] = (
            "Mycobacterial species identified. Reads too low to proceed to genome assembly."
        )
        mapping_json = read_json_file(reports["mapping"])
        mykrobe_data = read_json_file(reports["mykrobe"])
        name_mapping = pd.read_csv(reports["name_mapping"])
        output["Mycobacterium Results"] = generate_mycobacterium_results(
            mapping_json, mykrobe_data, name_mapping, "creation_report" in reports
        )
        output["Assembled NTM Results"] = generate_assembled_results(
            mapping_json, mykrobe_data, name_mapping, assembled_species
        )
    else:
        output["Mycobacterium Results"] = None
    # make this next block a list to cope with the future when other species are also mapped,
    # and potentially also have resistance predictions returned
    # FIXME for now we can hard code much of this since there will only ever be one and it will always
    # be M. tuberculosis
    if (
        "mapping" in reports
        and "creation_report" in reports
        and "gnomonicus" in reports
    ):
        output["Pipeline Outcome"] = (
            f"Sufficient reads mapped to {len(assembled_species)} species for genome assembly and resistance prediction."
        )
        creation_report_json = read_json_file(reports["creation_report"])
        gnom_json = read_json_file(reports["gnomonicus"])
        output["Genomes"] = []
        genome = {}
        genome["Name"] = "M. tuberculosis"
        genome["Sequencing Quality"] = generate_sequencing_quality(
            mapping_json, creation_report_json
        )
        genome["Resistance Prediction"] = generate_resistance_prediction(gnom_json)
        output["Genomes"].append(genome)
    else:
        output["Genomes"] = None  #
    if "versions" in reports or "knowledge" in reports:
        output["Metadata"] = {}
    if "versions" in reports:
        pipeline_build = read_pipeline_build(reports["versions"])
        output["Metadata"]["Pipeline build"] = pipeline_build
    if "knowledge" in reports:
        knowledge = read_json_file(reports["knowledge"])
        output["Metadata"]["Reference Data Files"] = knowledge

    if len(assembled_species) > 0:
        # Lots of these checks are TB specific, so override the pipeline outcome based on
        # the species spat out of clockwork
        output["Pipeline Outcome"] = (
            f"Sufficient reads mapped to {len(assembled_species)} species for genome assembly and resistance prediction."
        )

    return output


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
    with open(path, "r") as file:
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
    with open(path, "r") as file:
        return file.read().strip()


def write_summary(output: dict, location: Path = Path("Mega.json")) -> None:
    """Write summary to JSON file.

    Args:
        output (dict): Summary information.
        location (Path, optional): Path to write to. Defaults to "Mega.json".
    """
    with open(location, "w") as file:
        file.write(json.dumps(output, indent=4))


def collate_reports(cli_args: Arguments) -> dict:
    """Builds a dict of reports from the cli arguments.

    Args:
        cli_args (Arguments): Command line arguments.

    Returns:
        dict: Pipeline reports.
    """
    reports = {}
    try:
        reports["versions"] = cli_args.versions
    except AttributeError as error:
        logging.info(error)
    try:
        reports["knowledge"] = cli_args.knowledge
    except AttributeError as error:
        logging.info(error)
    reports["gatekeeper"] = cli_args.gatekeeper
    try:
        reports["mapping"] = cli_args.mapping
    except AttributeError as error:
        logging.info(error)
    try:
        reports["mykrobe"] = cli_args.mykrobe
    except AttributeError as error:
        logging.info(error)
    try:
        reports["creation_report"] = cli_args.creation_report
    except AttributeError as error:
        logging.info(error)
    try:
        reports["gnomonicus"] = cli_args.gnomonicus
    except AttributeError as error:
        logging.info(error)
    try:
        reports["name_mapping"] = cli_args.name_mapping
    except AttributeError as error:
        logging.info(error)
    return reports


def cli_entry_point() -> None:
    """CLI entry point."""
    cli_args = Arguments(sys.argv[1:])
    reports = collate_reports(cli_args)
    summary = create_summary(reports, assembled_species=cli_args.assembled_species)
    write_summary(summary, cli_args.output)
