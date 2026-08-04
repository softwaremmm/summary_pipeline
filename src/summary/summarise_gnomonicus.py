import numpy as np
import pandas as pd

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


def summarise_gnomonicus(gnomonicus_data: dict) -> dict:
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
        effects_muts_vars_df[
            ["coverage_ref", "coverage_alt"]
        ] = effects_muts_vars_df.apply(unpack_COV_from_info, axis=1)
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
