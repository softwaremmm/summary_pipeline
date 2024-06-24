"""Summay JSON output from GPAS"""

import json
import logging
import os
import sys
from pathlib import Path

import pandas
import numpy as np
from summary.cli_args import Arguments

logging.basicConfig(
    format="%(asctime)s — %(name)s — %(levelname)s — %(funcName)s:%(lineno)d — %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S%z",
    level=logging.DEBUG,
)

treatment_classes = {
    "First-line treatment": ["INH", "RIF", "PZA", "EMB"],
    "Second-line treatment": ["MXF", "LEV", "LZD", "BDQ"],
    "Reserve treatment": ["AMI", "KAN", "STM", "CAP", "ETH", "DLM"],
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
    mappings: dict, mykrobe_data: dict, name_mapping: pandas.DataFrame
) -> dict:
    """Summarises Competitive Mapping and Mykrobe outputs.

    Args:
        mappings (dict): Output from Competitive Mapping.
        mykrobe_data (dict): Output from Mykrobe.

    Returns:
        dict: Summary of Competitive Mapping and Mykrobe outputs.
    """
    myco = {
        "Summary": [],
        "Species": [],
        "Phylogenic Group": [],
        "Subspecies": [],
        "Lineage": [],
    }

    # Species (competitive mapping)
    mappings_sorted = pandas.DataFrame.from_dict(mappings).sort_values(
        by=["coverage"], ascending=False
    )
    tophit = mappings_sorted.head(1).to_dict(orient="records")[0]

    myco["Species"] = [
        {
            "Name": tophit["genome_name"],
            "Num Reads": int(tophit["numreads"]),
            "Coverage": tophit["coverage"],
            "Mean Depth": tophit["meandepth"],
            "Length": tophit["length"],
        }
    ]
    tophit_name = tophit["genome_name"]

    if mykrobe_data == {}:
        # If mykrobe doesn't return a species,
        # USE COMPETITIVE MAPPING

        summary_name = organism_name(tophit_name, name_mapping)

        myco["Summary"] = [
            {
                "Name": summary_name,
                "Num Reads": int(tophit["numreads"]),
                "Coverage": myco["Species"][0]["Coverage"],
                "Depth": myco["Species"][0]["Mean Depth"],
            }
        ]

        mixed_pop = False

    else:
        # Phylogenetic Group (mykrobe)
        myco["Phylogenic Group"] = process_phylo_group(mykrobe_data.get("phylo_group"))

        # "Subspecies" (mykrobe)
        if "species" in mykrobe_data:
            myco["Subspecies"] = process_subspecies(
                mykrobe_data.get("species")
            )  # Why is species assigned to subspecies?

        # Lineage (mykrobe)
        if "lineage" in mykrobe_data:
            myco["Lineage"] = process_lineages(mykrobe_data.get("lineage"))

        if len(myco["Phylogenic Group"]) == 2:
            mixed_pop = True
        elif len(myco["Phylogenic Group"]) > 2:
            raise ValueError("Mixed population with more than two phylo groups.")
        else:
            mixed_pop = False

        # Summary
        if tophit_name == "M.tuberculosis":
            # USE MYKROBE lineage and species information

            # Append lineage information from mykrobe to species name
            # from competitive mapping, if available
            if len(myco["Lineage"]) == 1:
                summary_name = organism_name(
                    tophit_name, name_mapping, myco["Lineage"][0]["Name"]
                )
            elif len(myco["Lineage"]) == 2:
                summary_name = organism_name(
                    tophit_name, name_mapping, myco["Lineage"][0]["Name"], True
                )
            else:
                # Default to just top hit if no lineage name exists
                summary_name = organism_name(tophit_name, name_mapping)

        elif tophit_name in [
            "M.intracellulare_chimaera",
            "M.avium_hominissuis",
            "M.paraintracellulare",
            "M.intracellulare",
            "M.lepraemurium",
            "M.abscessus",
        ]:
            # USE MYKROBE
            if mixed_pop:
                # Use competitive mapping
                summary_name = organism_name(tophit_name, name_mapping)

            else:
                # Use lineage name as species name
                summary_name = organism_name(
                    tophit_name, name_mapping, myco["Lineage"][0]["Name"]
                )

        elif myco["Species"][0]["Coverage"] < 40:
            # USE MYKROBE

            summary_name = organism_name(tophit_name, name_mapping)

        else:
            # USE COMPETITIVE MAPPING

            summary_name = organism_name(tophit_name, name_mapping)

        myco["Summary"] = [
            {
                "Name": summary_name,
                "Num Reads": int(tophit["numreads"]),
                "Coverage": myco["Species"][0]["Coverage"],
                "Depth": myco["Species"][0]["Mean Depth"],
            }
        ]

    # Always include TB, if present
    tb_row = mappings_sorted[mappings_sorted["genome_name"] == "M.tuberculosis"]
    if tb_row.empty is False:
        tb = tb_row.to_dict(orient="records")[0]
        if tb != tophit:
            myco["Species"].append(
                {
                    "Name": organism_name(tb["genome_name"], name_mapping),
                    "Num Reads": int(tb["numreads"]),
                    "Coverage": tb["coverage"],
                    "Mean Depth": tb["meandepth"],
                    "Length": tb["length"],
                }
            )
            myco["Summary"].append(
                {
                    "Name": organism_name(tb["genome_name"], name_mapping),
                    "Num Reads": int(tb["numreads"]),
                    "Coverage": tb["coverage"],
                    "Depth": tb["meandepth"],
                }
            )

    # Include 1st runner up in a mixed population
    # with TB winner
    if tophit_name == "M.tuberculosis" and mixed_pop:
        second_hit = mappings_sorted.head(2).to_dict(orient="records")[1]
        myco["Summary"].append(
            {
                "Name": organism_name(second_hit["genome_name"], name_mapping),
                "Num Reads": int(second_hit["numreads"]),
                "Coverage": second_hit["coverage"],
                "Depth": second_hit["meandepth"],
            }
        )

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
    """Summarise mykrobe lineages output

    Args:
        lineages (dict): Lineages information from mykrobe

    Returns:
        list[dict]: List of lineage summaries
    """
    lineage_summary = []
    if "lineage" in lineages:
        for lineage_name in lineages.get("lineage"):
            calls = lineages.get("calls")
            specific_line = calls.get(lineage_name)
            # TODO: Needs review. Trying to be generic,
            # should this come from the first item in the list???
            # TODO: This section also needs better error handling
            top_level = list(specific_line.keys())[0]
            variant_level = specific_line.get(top_level)
            variant_name = list(variant_level.keys())[0]
            info_level = variant_level.get(variant_name)
            # TODO: Chained getfields would be nicer...Or better generic handling of this
            info = info_level.get("info")
            cov = info.get("coverage")
            ref = cov.get("reference")
            coverage = ref.get("percent_coverage")
            mediandepth = ref.get("median_depth")
            new_line = {
                "Name": lineage_name,
                "Coverage": coverage,
                "Median Depth": mediandepth,
            }
            lineage_summary.append(new_line)

    else:
        for lineage_name in lineages:
            new_line = {
                "Name": lineage_name,
                "Coverage": lineages[lineage_name]["percent_coverage"],
                "Median Depth": lineages[lineage_name]["median_depth"],
            }
            lineage_summary.append(new_line)

    return lineage_summary


def organism_name(
    cm_name: str,
    mapping: pandas.DataFrame,
    lineage: str = "Unknown",
    mixed_tb_lineage: bool = False,
) -> str:
    """Determine the name to report for the organism.

    Args:
        cm_name (str): Name from Competitive Mapping.
        mapping (pandas.DataFrame): Reference data mapping Competitive Mapping
        and mykrobe outputs to reportable name.
        lineage (str, optional): Lineage from mykrobe. Defaults to "Unknown".
        mixed_tb_lineage (bool, optional): True if mykrobe reports multiple lineages. Defaults to False

    Returns:
        str: Reportable name for the organism.
    """
    # This is a special case of more than one TB linage
    # we may wish to report both lineages in future, but
    # for now we simply report the run as "mixed".
    if cm_name == "M.tuberculosis" and mixed_tb_lineage is True:
        return "M.tuberculosis (mixed lineage)"
    # Lookup name by Compatitive Mapping name and mykrobe
    # lineage.
    name_df = mapping[(mapping.reference == cm_name) & (mapping.LINEAGE == lineage)]
    if name_df.empty:
        # This means the name we're seeking isn't in the lookup table
        name = cm_name
    else:
        # Multiple names identical names are returned where mykrobe
        # indentifies an alternate species associated with a single species
        # in competitive mapping e.g. "Mycobacterium_algericum" or
        # "Mycobacterium_algericum_A" are both associated with
        # "M.algericus". We ignore this information from mykrobe.
        name = pandas.unique(name_df.REPORT).item()
        # If more than one unique name is returned, it will cause an
        # error.

    return name


def generate_sequencing_quality(mappings: dict, genome_creation_report: dict) -> dict:
    """Summarises sequencing quality.

    Args:
        mappings (dict): Competitive Mapping output.

    Returns:
        dict: Summary of sequencing quality.
    """
    # Much of this data is a repeat of data already in Myco Results
    tb_mappings = list(
        filter(lambda mapping: "tuberculosis" in mapping["genome_name"], mappings)
    )
    if len(tb_mappings) > 1:
        raise ValueError(
            "More than one mapping to M.tuberculosis. Possible manifest problem."
        )
    tb_mapping = tb_mappings[0]

    seq_qual = {
        "Mapped To": tb_mapping["genome_name"],
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


def construct_payload(significant_variants_df: pandas.DataFrame) -> list:
    """Construct Resistance Prediction Details payload for the summary JSON.

    Args:
        significant_variants_df (pandas.DataFrame):

    Returns:
        list: results for incorporation in summary JSON
    """

    drugs = []
    payload = []
    valid_nucleotides = ["a", "t", "c", "g", "x", "z"]

    # TODO: tried to do more elegantly with pandas.to_json() but ended up doing simply

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

        if pandas.isnull(row.gene):
            significant_variant["Gene"] = None
        else:
            significant_variant["Gene"] = row.gene

        significant_variant["Mutation"] = row.mutation

        if pandas.isnull(row.gene_position):
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

        significant_variant["Coverage"] = [
            int(row.coverage_ref)
            if row.coverage_ref is not None and row.coverage_ref >= 0
            else None,
            int(row.coverage_alt)
            if row.coverage_alt is not None and row.coverage_alt >= 0
            else None,
        ]

        if seen_mutations.get((row.drug, significant_variant["Gene"], significant_variant["Mutation"])):
            # Already seen this mutation so check if this is variant's coverage is less
            old_idx, significant_cov = seen_mutations.get((row.drug, significant_variant["Gene"], significant_variant["Mutation"]))
            if significant_cov[0] is not None:
                if significant_variant["Coverage"][0] is not None:
                    if significant_variant["Coverage"][0] > significant_cov[0]:
                        keep = False
                else:
                    # Last row for this codon gave a specific value, this didn't, so don't keep this
                    keep = False
            if significant_cov[1] is not None:
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
        seen_mutations[(row.drug, significant_variant["Gene"], significant_variant["Mutation"])] = (len(drug_blocks[row.drug]["Mutations"])-1, significant_variant["Coverage"])

    for drug_name in drugs:
        payload.append(drug_blocks[drug_name])

    return payload


def unpack_COV_from_info(row: pandas.Series) -> pandas.Series:
    """Helper pandas function for retrieving the COV from the INFO column

    Args:
        row (pandas.Series): row passed from pandas apply function

    Returns:
        pandas.Series: REF and ALT coverage values
    """
    result = pandas.Series([np.float64("nan"), np.float64("nan")])
    if row.vcf_idx is not None and row.vcf_idx >= 0:
        idx = int(row.vcf_idx)
        if "COV" in row.vcf_evidence:
            if len(row.vcf_evidence["COV"]) == 1:
                # Edge case of only one COV value
                if idx == 0:
                    # It's a ref (probably a null) so put in just the ref coverage
                    result = pandas.Series([row.vcf_evidence["COV"][0], 0])
                else:
                    # It's an alt (probably a null) so put in just the alt coverage
                    result = pandas.Series([0, row.vcf_evidence["COV"][idx]])
            else:
                if idx == 0:
                    # It's a ref (probably a null) so put in the ref coverage
                    result = pandas.Series([row.vcf_evidence["COV"][0], 0])
                else:
                    # It's not a ref call, so give ref and alt coverage
                    result = pandas.Series(
                        [row.vcf_evidence["COV"][0], row.vcf_evidence["COV"][idx]]
                    )
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
            if drug3 in raw_antibiogram.keys():
                drug_name_long = drug_names[drug3] + " (" + drug3 + ")"
                antibiogram[treatment_category][drug_name_long] = raw_antibiogram[drug3]

    amr["Resistance Prediction Summary"] = antibiogram

    # Check if we have situtation 1 or 2
    if len(data.get("effects")) == 0:
        # Situation 2 - no variants
        amr["Resistance Prediction Detail"] = []
    else:
        # Situation 1 - variants

        # retrieve the effects block and build our base pandas DataFrame
        effects = data.get("effects")
        effects_list = []
        for drug_name in effects:
            for effect_mutation in effects[drug_name]:
                if "phenotype" not in effect_mutation:
                    effect_mutation["drug"] = drug_name
                    effects_list.append(effect_mutation)
        effects_df = pandas.DataFrame(effects_list)
        effects_df.set_index(["gene", "mutation"], inplace=True)

        # retrieve the mutations block and build another pandas DataFrame
        mutations_list = data.get("mutations")
        mutations_df = pandas.DataFrame(mutations_list)
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
        variants_df = pandas.DataFrame(variants)
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

        # use the pandas helper function defined elsewhere to extract COV from the vcf_evidence field
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

        # effects_muts_vars_df.set_index("drug", inplace=True)
        payload = construct_payload(effects_muts_vars_df)
        amr["Resistance Prediction Detail"] = payload

    return amr


def create_summary(
    reports: dict,
) -> dict:
    """Summarises GPAS pipeline output.

    Args:
        reports (dict): A collection of reports to summarise.

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
            "Mycobacterial species identified. Reads mapped to M. tuberculosis (H37Rv v3) too low to proceed to M. tuberculosis complex genome assembly."
        )
        mapping_json = read_json_file(reports["mapping"])
        mykrobe_data = read_json_file(reports["mykrobe"])
        name_mapping = pandas.read_csv(reports["name_mapping"])
        output["Mycobacterium Results"] = generate_mycobacterium_results(
            mapping_json, mykrobe_data, name_mapping
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
            "Sufficient reads mapped to M. tuberculosis (H37Rv v3) for genome assembly, resistance prediction and relatedness assessment."
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
        return file.read()


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
    summary = create_summary(reports)
    write_summary(summary, cli_args.output)
