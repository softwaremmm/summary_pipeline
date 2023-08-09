"""Summay JSON output from GPAS"""


import logging
import json
import os
from pathlib import Path
import pandas

from summary.reports import ReportList, ReportType

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
        "Unclassified Reads": gatekeeper_data.get("Unclassified"),
        "Non-Mycobacterium Bacteria Reads": None,
        "Mycobacterium Reads": gatekeeper_data.get("Mycobacteriaceae"),
    }
    logging.warning("Human read data not supported in this version")
    bac = gatekeeper_data.get("Bacteria")
    if bac and organism["Mycobacterium Reads"]:
        organism["Non-Mycobacterium Bacteria Reads"] = (
            bac - organism["Mycobacterium Reads"]
        )
    return organism


def generate_mycobacterium_results(mappings: dict, mykrobe_data: dict) -> dict:
    """Summarises Competitive Mapping and Mykrobe outputs.

    Args:
        mappings (dict): Output from Competitive Mapping.
        mykrobe_data (dict): Output from Mykrobe.

    Raises:
        ValueError: Multiple phylo groups.
        ValueError: Multiple species groups.

    Returns:
        dict: Summary of Competitive Mapping and Mykrobe outputs.
    """
    myco = {
        "Summary": [],
        "Species": [],
        "Phylogenic Group": {},
        "Subspecies": {},
        "Lineage": [],
    }
    # Competitive mapping
    for mapping in mappings:
        genome_name = mapping.get("genome_name").replace(" complete genome", "")
        gen_reads = mapping.get("numreads")
        coverage = mapping.get("coverage")
        meandepth = mapping.get("meandepth")
        length = mapping.get("length")
        if coverage > 80 or "tuberculosis" in genome_name:
            new_species = {
                "Name": genome_name,
                "Num Reads": int(gen_reads),
                "Coverage": coverage,
                "Mean Depth": meandepth,
                "Length": length,
            }
            myco["Species"].append(new_species)
    # Mykrobe
    phylo_group = mykrobe_data.get("phylo_group")
    if not len(phylo_group.keys()) == 1:
        raise ValueError(
            "Require only 1 phylo group. Found " + str(len(phylo_group.keys()))
        )
    myco["Phylogenic Group"]["Name"] = list(phylo_group.keys())[0]
    myco["Phylogenic Group"]["Coverage"] = phylo_group[
        myco["Phylogenic Group"]["Name"]
    ].get("percent_coverage")
    myco["Phylogenic Group"]["Median Depth"] = phylo_group[
        myco["Phylogenic Group"]["Name"]
    ].get("median_depth")
    subspecies = mykrobe_data.get("species")  # Why is species assigned to subspecies?
    if not len(subspecies.keys()) == 1:
        raise ValueError(
            "Require only 1 species group. Found " + str(len(subspecies.keys()))
        )
    myco["Subspecies"]["Name"] = list(subspecies.keys())[0]
    myco["Subspecies"]["Coverage"] = subspecies[myco["Subspecies"]["Name"]].get(
        "percent_coverage"
    )
    myco["Subspecies"]["Median Depth"] = subspecies[myco["Subspecies"]["Name"]].get(
        "median_depth"
    )
    lineages = mykrobe_data.get("lineage")
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
        myco["Lineage"].append(new_line)

        # if Mykrobe has returned one or more lineages we must be dealing with MTB
        lineage_number = lineage_name.split("lineage")[1]
        new_summary = {
            "Name": "M. tuberculosis (Lineage " + lineage_number + ")",
            "Coverage": float(coverage),
            "Depth": float(mediandepth),
        }
        myco["Summary"].append(new_summary)

    # now iterate through the species detected by competitive mapping, ignoring MTB
    # on the assumption that is has been picked up by Mykrobe
    for detected_species in myco["Species"]:
        # skip over MTB
        if "tuberculosis" not in detected_species["Name"]:
            new_summary = {
                "Name": detected_species["Name"],
                "Coverage": float(detected_species["Coverage"]),
                "Depth": float(detected_species["Mean Depth"]),
            }
            myco["Summary"].append(new_summary)

    return myco


def generate_sequencing_quality(mappings: dict) -> dict:
    """Summarises sequencing quality.

    Args:
        mappings (dict): Competitive Mapping output.

    Returns:
        dict: Summary of sequencing quality.
    """
    # Much of this data is a repeat of data already in Myco Results
    for mapping in mappings:
        genome_name = mapping.get("genome_name").replace(" complete genome", "")
        if "tuberculosis" in genome_name:
            seq_qual = {
                "Mapped To": mapping.get("#rname"),
                "Num Reads": mapping.get("numreads"),
                "Coverage": mapping.get("coverage"),
                "Mean Depth": mapping.get("meandepth"),
                # FIXME: below is a placeholder for the number of mixed ("het") calls
                # found in the gVCF which gives you an indication of sample quality
                "Mixed calls": 0,
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
    drugs = significant_variants_df.index.unique()
    drugs = sorted(drugs)

    drug_blocks = {}
    for drug in drugs:
        drug_blocks[drug] = {"Drug Name": drug, "Mutations": []}

    for idx, row in significant_variants_df.iterrows():
        significant_variant = {}
        significant_variant["Gene"] = row.gene
        significant_variant["Mutation"] = row.mutation
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
        if row.coverage_ref >= 0 and row.coverage_alt >= 0:
            significant_variant["Coverage"] = [
                int(row.coverage_ref),
                int(row.coverage_alt),
            ]
        else:
            significant_variant["Coverage"] = [None, None]
        significant_variant["Prediction"] = row.prediction
        if row.evidence == {}:
            significant_variant["Evidence"] = ""
        else:
            significant_variant["Evidence"] = row.evidence

        drug_blocks[idx]["Mutations"].append(significant_variant)

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
    result = pandas.Series([None, None])
    if row.vcf_idx >= 0:
        idx = int(row.vcf_idx)
        if "COV" in row.vcf_evidence:
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
    # let's put the drugs in alphabetical order
    raw_antibiogram = dict(sorted((data.get("antibiogram")).items()))
    # add BDQ as a placeholder as it will be in e.g. version 2 of the WHO catalogue when it arrives
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
    effects_muts_vars_df[["coverage_ref", "coverage_alt"]] = effects_muts_vars_df.apply(
        unpack_COV_from_info, axis=1
    )
    effects_muts_vars_df.drop(columns=["vcf_evidence", "vcf_idx"], inplace=True)

    # ignore mutations that have no effect
    effects_muts_vars_df = effects_muts_vars_df[effects_muts_vars_df.prediction != "S"]

    # now we have a DataFrame with all the fields and so can construct the dict payload
    effects_muts_vars_df.reset_index(inplace=True)
    effects_muts_vars_df.set_index("drug", inplace=True)
    payload = construct_payload(effects_muts_vars_df)
    amr["Resistance Prediction Detail"] = payload

    return amr


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


def create_summary(
    reports: ReportList,
) -> dict:
    """Summarises GPAS pipeline output.

    Args:
        reports (ReportList): A collection of reports to summarise.

    Returns:
        dict: Summary GPAS pipeline output.
    """
    output = {}
    if [
        reports.contains(ReportType.GATEKEEPER),
        reports.contains(ReportType.MAPPING),
        reports.contains(ReportType.MYKROBE),
        reports.contains(ReportType.GNOMONICUS),
    ] == [True, False, False, False]:
        # Not enough mycobacterial reads
        pass
    elif [
        reports.contains(ReportType.GATEKEEPER),
        reports.contains(ReportType.MAPPING),
        reports.contains(ReportType.MYKROBE),
        reports.contains(ReportType.GNOMONICUS),
    ] == [True, True, True, False]:
        # Not enough TB reads
        pass
    elif [
        reports.contains(ReportType.GATEKEEPER),
        reports.contains(ReportType.MAPPING),
        reports.contains(ReportType.MYKROBE),
        reports.contains(ReportType.GNOMONICUS),
    ] == [True, True, True, True]:
        gatekeeper_json = reports.retrieve(ReportType.GATEKEEPER).report_contents
        mapping_json = reports.retrieve(ReportType.MAPPING).report_contents
        mykrobe_json = reports.retrieve(ReportType.MYKROBE).report_contents
        gnom_json = reports.retrieve(ReportType.GNOMONICUS).report_contents
    else:
        raise ValueError(
            "Summary cannot be generated from this combination of reports: "
            + str(reports)
        )

    if reports.contains(ReportType.GATEKEEPER):
        output["Organism Identification"] = generate_organism_identification(
            gatekeeper_json
        )
    else:
        output = "Pipeline failed to produce a summary (summary_pipeline could not find gatekeeper report)."
    if reports.contains(ReportType.MAPPING) and reports.contains(ReportType.MYKROBE):
        output["Mycobacterium Results"] = generate_mycobacterium_results(
            mapping_json, mykrobe_json
        )
    else:
        output["Mycobacterium Results"] = {
            "Insufficient reads",
            "There were insufficient mycobacterial reads to carry out competitive mapping or lineage calling.",
        }
    # make this next block a list to cope with the future when other species are also mapped,
    # and potentially also have resistance predictions returned
    # FIXME for now we can hard code much of this since there will only ever be one and it will always
    # be M. tuberculosis
    if reports.contains(ReportType.MAPPING) and reports.contains(ReportType.GNOMONICUS):
        output["Genomes"] = []
        genome = {}
        genome["Name"] = "M. tuberculosis"
        genome["Sequencing Quality"] = generate_sequencing_quality(mapping_json)
        genome["Resistance Prediction"] = generate_resistance_prediction(gnom_json)
        output["Genomes"].append(genome)
    else:
        output["Genomes"] = {
            "Insufficient reads",
            "There were insufficient Mycobacterium tuberculosis reads to determine sequencing quality or predict antibiotic resistances.",
        }

    return output


def write_summary(output: dict, location: Path = Path("Mega.json")) -> None:
    """Write summary to JSON file.

    Args:
        output (dict): Summary information.
        location (Path, optional): Path to write to. Defaults to "Mega.json".
    """
    with open(location, "w") as file:
        file.write(json.dumps(output, indent=4))


def summarise(cli_args) -> None:
    reports = ReportList(
        [cli_args.gatekeeper, cli_args.mapping, cli_args.mykrobe, cli_args.gnomonicus]
    )
    summary = create_summary(reports)
    write_summary(summary, cli_args.output)
