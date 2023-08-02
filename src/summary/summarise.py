import logging
import json
import argparse
import os
from pathlib import Path


def generate_organism_identification(gatekeeper_data, fail_hard):
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


def generate_mycobacterium_results(mappings, mykrobe_data, fail_hard):
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
    if not (len(phylo_group.keys()) == 1):
        raise ValueError(
            "Require only 1 phylo group. Found " + str(len(phylo_group.keys()))
        )
    else:
        myco["Phylogenic Group"]["Name"] = list(phylo_group.keys())[0]
        myco["Phylogenic Group"]["Coverage"] = phylo_group[
            myco["Phylogenic Group"]["Name"]
        ].get("percent_coverage")
        myco["Phylogenic Group"]["Median Depth"] = phylo_group[
            myco["Phylogenic Group"]["Name"]
        ].get("median_depth")
    subspecies = mykrobe_data.get("species")  # Why is species assigned to subspecies?
    if not (len(subspecies.keys()) == 1):
        raise ValueError(
            "Require only 1 species group. Found " + str(len(subspecies.keys()))
        )
    else:
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
        # TODO: Needs review. Trying to be generic, should this come from the first item in the list???
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


def generate_sequencing_quality(mappings, fail_hard):
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


def generate_resistance_prediction(gnomonicus_data, fail_hard):
    amr = {"Resistance Prediction Summary": {}, "Resistance Prediction Detail": []}
    data = gnomonicus_data.get("data")
    # reformat data to make search easier later
    all_mutations_details = {}
    mutations_list = data.get("mutations")
    for mutation in mutations_list:
        mutation_name = mutation.get("mutation")
        if mutation_name:
            all_mutations_details[mutation_name] = mutation
    # reformat data to make search easier later
    all_gene_name_pos_res = {}
    variants = data.get("variants")
    for variant in variants:
        gene_name = variant.get("gene_name")
        gene_position = variant.get("gene_position")
        vcf = variant.get("vcf_evidence")
        cov = vcf.get("COV")
        if gene_name not in all_gene_name_pos_res.keys():
            all_gene_name_pos_res[gene_name] = {}
        all_gene_name_pos_res[gene_name][gene_position] = cov
    amr["Resistance Prediction Summary"] = data.get("antibiogram")
    effects = data.get("effects")
    for drug in effects.keys():
        new_drug = {"Drug Name": drug, "Mutations": []}
        interesting_mutants = []
        for mutant in effects[drug]:
            mutant_data = mutant.get(
                "prediction"
            )  # this is horrible as it will throw errors for pheno data
            if mutant_data and not mutant_data == "S":
                interesting_mutants.append(mutant)
        for im in interesting_mutants:
            gene = im.get("gene")
            new_mutation = im.get("mutation")
            prediction = im.get("prediction")
            ref_to_alt = None
            position = None
            cov = None
            if new_mutation in all_mutations_details.keys():
                position = all_mutations_details[new_mutation].get("gene_position")
                ref = all_mutations_details[new_mutation].get("ref")
                alt = all_mutations_details[new_mutation].get("alt")
                if ref and alt:
                    ref_to_alt = ref + "->" + alt
            else:
                raise ValueError("Mutation not in mutations list: " + new_mutation)
            if gene in all_gene_name_pos_res.keys():
                if position in all_gene_name_pos_res[gene].keys():
                    cov = all_gene_name_pos_res[gene][position]
                else:
                    raise ValueError(
                        "Position not in gene position list: "
                        + gene
                        + " "
                        + str(position)
                    )
            else:
                raise ValueError("Gene not in genes list: " + gene)
            new_drug["Mutations"].append(
                {
                    "Gene": gene,
                    "Position": position,
                    "Ref to Alt": ref_to_alt,
                    "Cov": cov,
                    "Prediction": prediction,
                }
            )
        amr["Resistance Prediction Detail"].append(new_drug)
    return amr


def should_fail_hard(fail_hard):
    if fail_hard:
        logging.error("Fail hard enabled. Exiting....")
        exit(1)


def read_json_file(path, fail_hard):
    if not (os.path.isfile(path)):
        logging.error("File " + path + " does not exist. Data could not be loaded")
        should_fail_hard(fail_hard)
    with open(path, "r") as f:
        data = json.load(f)
    return data


def create_summary(
    gatekeeper: Path,
    mapping: Path,
    mykrobe: Path,
    gnomonicus: Path,
    fail_hard: bool = False,
) -> dict:
    output = {}
    # output["Sample Details"] = generate_sample_details()
    gatekeeper_json = read_json_file(gatekeeper, fail_hard)
    mapping_json = read_json_file(mapping, fail_hard)
    mykrobe_json = read_json_file(mykrobe, fail_hard)
    gnom_json = read_json_file(gnomonicus, fail_hard)
    output["Organism Identification"] = generate_organism_identification(
        gatekeeper_json, fail_hard
    )
    output["Mycobacterium Results"] = generate_mycobacterium_results(
        mapping_json, mykrobe_json, fail_hard
    )
    output["Sequencing Quality"] = generate_sequencing_quality(mapping_json, fail_hard)
    output["Resistance Prediction"] = generate_resistance_prediction(
        gnom_json, fail_hard
    )
    return output


def write_summary(output: dict, location: Path = "Mega.json"):
    with open(location, "w") as f:
        f.write(json.dumps(output, indent=4))


def summarise() -> None:
    logging.basicConfig(
        format="%(asctime)s — %(name)s — %(levelname)s — %(funcName)s:%(lineno)d — %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S%z",
    )
    parser = argparse.ArgumentParser(
        description="Process pipeline output to create mega.json"
    )
    parser.add_argument(
        "--fail_hard", dest="fail_hard", action="store_true", default=False
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
