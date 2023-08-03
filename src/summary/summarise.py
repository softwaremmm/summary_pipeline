"""Summay JSON output from GPAS"""

import logging
import json
import argparse
import os
from pathlib import Path
import pandas

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
    myco = {"Species": [], "Phylogenic Group": {}, "Subspecies": {}, "Lineage": []}
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
            }
    return seq_qual


def construct_payload(df: pandas.DataFrame) -> list:
    """Construct Resistance Prediction Details payload for the summary JSON.

    Args:
        df (pandas.DataFrame):

    Returns:
        list: results for incorporation in summary JSON
    """

    drugs=[]
    payload = []
    entry = {}
    valid_nucleotides = ['a', 't', 'c', 'g', 'x', 'z']

    # TODO: tried to do more elegantly with pandas.to_json() but ended up doing simply

    # create an alphabetical list of the drugs
    drugs = df.index.unique()
    drugs = sorted(drugs)

    drug_blocks = {}
    for drug in drugs:
        drug_blocks[drug] = {"Drug Name": drug, "Mutations": []}

    for idx,row in df.iterrows():

        result = {}
        result['Gene'] = row.gene
        result['Mutation'] = row.mutation
        result['Position'] = int(row.gene_position)
        if isinstance(row.ref, str):
            result['Ref']= row.ref
        elif row.mutation[0] in valid_nucleotides and row.mutation[-1] in valid_nucleotides:
            result['Ref'] = row.mutation[0]
        else:
            result['Ref'] = ''
        if isinstance(row.alt, str):
            result['Alt']= row.alt
        elif row.mutation[0] in valid_nucleotides and row.mutation[-1] in valid_nucleotides:
            result['Alt'] = row.mutation[-1]
        else:
            result['Alt'] = ''
        if row.coverage_ref>=0 and row.coverage_alt>=0:
            result['Coverage'] = [int(row.coverage_ref), int(row.coverage_alt)]
        else:
            result['Coverage'] = [None, None]
        result['Prediction'] = row.prediction
        if row.evidence == {}:
            result['Evidence'] = ''
        else:
            result['Evidence'] = row.evidence

        drug_blocks[idx]['Mutations'].append(result)

    for drug_name in drugs:
        payload.append(drug_blocks[drug_name])

    return(payload)


def unpack_info(row: pandas.Series) -> pandas.Series:
    """Helper pandas function for retrieving the COV from the INFO column

    Args:
        row (pandas.Series): row passed from pandas apply function

    Returns:
        pandas.Series: REF and ALT coverage values
    """
    if row.vcf_idx>=0:
        idx = int(row.vcf_idx)
        if 'COV' in row.vcf_evidence:
            return(pandas.Series([row.vcf_evidence['COV'][0],row.vcf_evidence['COV'][idx]]))
        else:
            return(pandas.Series([None,None]))
    else:
        return(pandas.Series([None,None]))

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
    antibiogram = dict(sorted((data.get("antibiogram")).items()))
    amr["Resistance Prediction Summary"] = antibiogram
    
    # retrieve the effects block and build our base pandas DataFrame 
    effects = data.get("effects")
    effects_list=[]
    for drug_name in effects:
        for effect_mutation in effects[drug_name]:
            if 'phenotype' not in effect_mutation:
                effect_mutation['drug']=drug_name
                effects_list.append(effect_mutation)
    effects_df = pandas.DataFrame(effects_list)
    effects_df.set_index(['gene', 'mutation'], inplace=True)

    # retrieve the mutations block and build another pandas DataFrame
    mutations_list = data.get("mutations")
    mutations_df = pandas.DataFrame(mutations_list)
    mutations_df.set_index(['gene', 'mutation'], inplace=True)

    # now left-join mutations to effects so we can get the a few extra columns
    # note that this can be many:1 since a single mutation can affect multiple drugs
    df = effects_df.join(mutations_df[['ref', 'alt', 'gene_position']])
    df.reset_index(inplace=True)
    df.set_index(['gene', 'gene_position'], inplace=True)

    # finally, retrieve the variants block and build the final DataFrame
    variants = data.get("variants")
    variants_df = pandas.DataFrame(variants)
    variants_df.rename(columns={'gene_name': 'gene'}, inplace=True)
    variants_df.set_index(['gene', 'gene_position'], inplace=True)

    # now left-join to variants so we can get at the INFO field held in vcf_evidence as this contains COV
    # note this can be 1:many since a single mutation can be made up of multiple variants (e.g. multiple SNPs, minor alleles etc)
    df = df.join(variants_df[['vcf_evidence', 'vcf_idx']])
    df.reset_index(inplace=True)
    df.set_index(['drug', 'gene', 'mutation'], inplace=True)

    # use the pandas helper function defined elsewhere to extract COV from the vcf_evidence field
    df[['coverage_ref', 'coverage_alt']] = df.apply(unpack_info, axis=1)
    df.drop(columns=['vcf_evidence', 'vcf_idx'], inplace=True)

    # ignore mutations that have no effect
    df = df[df.prediction!='S']

    # now we have a DataFrame with all the fields and so can construct the dict payload
    df.reset_index(inplace=True)
    df.set_index('drug', inplace=True)
    payload = construct_payload(df)
    amr["Resistance Prediction Detail"]=payload

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
    gatekeeper: Path,
    mapping: Path,
    mykrobe: Path,
    gnomonicus: Path,
) -> dict:
    """Summarises GPAS pipeline output.

    Args:
        gatekeeper (Path): Path to Gatekeeper report.
        mapping (Path): Path to Competitive Mapping report.
        mykrobe (Path): Path to Mykrobe report.
        gnomonicus (Path): Path to gnomonicus report.

    Returns:
        dict: Summary GPAS pipeline output.
    """
    output = {}
    gatekeeper_json = read_json_file(gatekeeper)
    mapping_json = read_json_file(mapping)
    mykrobe_json = read_json_file(mykrobe)
    gnom_json = read_json_file(gnomonicus)
    output["Organism Identification"] = generate_organism_identification(
        gatekeeper_json
    )
    output["Mycobacterium Results"] = generate_mycobacterium_results(
        mapping_json, mykrobe_json
    )
    output["Sequencing Quality"] = generate_sequencing_quality(mapping_json)
    output["Resistance Prediction"] = generate_resistance_prediction(gnom_json)
    return output


def write_summary(output: dict, location: Path = Path("Mega.json")) -> None:
    """Write summary to JSON file.

    Args:
        output (dict): Summary information.
        location (Path, optional): Path to write to. Defaults to "Mega.json".
    """
    with open(location, "w") as file:
        file.write(json.dumps(output, indent=4))


def summarise() -> None:
    """CLI entry point."""
    logging.basicConfig(
        format="%(asctime)s — %(name)s — %(levelname)s — %(funcName)s:%(lineno)d — %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S%z",
    )
    parser = argparse.ArgumentParser(
        description="Process pipeline output to create mega.json"
    )
    parser.add_argument(
        "--gatekeeper", dest="gatekeeper", help="Path to gatekeeper_report.json file"
    )
    parser.add_argument(
        "--mapping", dest="mapping", help="Path to competitivemapping_report.json file"
    )
    parser.add_argument(
        "--mykrobe", dest="mykrobe", help="Path to mykrobe_report.json file"
    )
    parser.add_argument(
        "--gnomonicus", dest="gnomonicus", help="Path to gnomonicus.json file"
    )
    parser.add_argument(
        "--output_path",
        default="Mega.json",
        dest="output",
        help="Path including name for output .json file",
    )
    args = parser.parse_args()
    summary = create_summary(
        args.gatekeeper, args.mapping, args.mykrobe, args.gnomonicus
    )
    write_summary(summary, args.output)
