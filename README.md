# Summary Pipeline

Summarises output from sub-workflows (part of WP8).

## Installation

1. Clone this repository
2. Create a conda environment `conda create -f -y -n summary_pipeline python=3.11`
3. Activate the conda environment e.g. `conda activate summary_pipeline`
4. Install this software `pip install .` (use `pip install -e .[dev]` for development)

## Conventional Commits
Use [conventional commits](https://www.conventionalcommits.org/en/v1.0.0/) when developing for this repo.
You should install the pre-commit hooks to check your commit messages. This can be done using the tool `pre-commit` which is a dev dependency in the `pyproject.toml`.
You can also use `commitizen` (another dev dependency) to help with writing conventional commits.

To install hooks run
```bash
pre-commit install --hook-type commit-msg
pre-commit install # to get other hooks for formatting etc
```

To make commit with commitizen run
```bash
cz c
```

## Tags and Releases

[Commitizen](https://commitizen-tools.github.io/commitizen/) is used to manage versioning of releases. This tool
can be used to make commits to this repository. Regardless, [conventional commits](https://www.conventionalcommits.org/en/v1.0.0/)
are required to ensure correct version numbering and changelog population.

**Do not add tags by hand.**

On merging a Pull Request a [GitHub action will run](.github/workflows/version.yaml), causing Commitizen to:
* Determine the new [semver](https://semver.org/) based on conventional commits.
* Replace the previous semver in [pyproject.toml](pyproject.toml) and other files as specified therein.
* Update the [CHANGELOG](CHANGELOG.md) based on commit messages.
* Commit these changes to the `main` branch.
* Create a tag for this commit with the tag name of the newly determined semver.
* Build a docker container for this new tag
* Create a new release from this tag.

There is a workflow for manually triggering a docker build action.
This shouldn't be required unless something has gone wrong with the commitizen action.


## Usage

```{bash}
conda activate summary_pipeline
```

### Python (via CLI)

#### Specify individual report files

```{bash}
summary_json --gatekeeper test_data/WTCHG_885333_73205296_1/speciation_report.json --mapping test_data/WTCHG_885333_73205296_1/species_comparison_report.json --mykrobe test_data/WTCHG_885333_73205296_1/subspecies_report.json --gnomonicus test_data/WTCHG_885333_73205296_1/tb/resistance_prediction_report.json --knowledge test_data/WTCHG_885333_73205296_1/knowledge.json --versions test_data/WTCHG_885333_73205296_1/PIPELINE_BUILD --creation_report test_data/WTCHG_885333_73205296_1/genome_creation_report.json --name_mapping test_data/reference/name_mapping.csv
```

All arguments are mandatory. This functionality is not used by the NextFlow pipeline and may be removed in future.

#### Pass report files as a list

```{bash}
summary_json --reports test_data/WTCHG_885333_73205296_1/PIPELINE_BUILD test_data/WTCHG_885333_73205296_1/speciation_report.json test_data/WTCHG_885333_73205296_1/species_comparison_report.json test_data/WTCHG_885333_73205296_1/subspecies_report.json test_data/WTCHG_885333_73205296_1/tb/resistance_prediction_report.json test_data/WTCHG_885333_73205296_1/genome_creation_report.json test_data/WTCHG_885333_73205296_1/knowledge.json test_data/reference/name_mapping.csv
```

### NextFlow

```{bash}
nextflow run . --reports test_data/WTCHG_885333_73205296_1/PIPELINE_BUILD,test_data/WTCHG_885333_73205296_1/speciation_report.json,test_data/WTCHG_885333_73205296_1/species_comparison_report.json,test_data/WTCHG_885333_73205296_1/subspecies_report.json,test_data/WTCHG_885333_73205296_1/tb/resistance_prediction_report.json,test_data/WTCHG_885333_73205296_1/genome_creation_report.json,test_data/WTCHG_885333_73205296_1/knowledge.json,test_data/reference/name_mapping.csv
```
### Running tests

Install for development and run `pytest`. No NextFlow tests are yet present.

### Test Data

Descriptions of test data. List / descriptions may be incomplete, but hopefully still helpful.

| Test Data Directory                        | Description                                                                                    |
| ------------------------------------------ | ---------------------------------------------------------------------------------------------- |
| [test_data/BCG]                            | MTB complex, _M. bovis_                                                                        |
| [test_data/covid]                          | Covid                                                                                          |
| [test_data/covid_no_meta]                  | Covid but without a pipeline versions file                                                     |
| [test_data/malmoense_over_40pc]            | _M. malmoense_, more than 40% coverage by competitive mapping                                  |
| [test_data/mix_ntm_win]                    | A mykrobe mixed result with an NTM as the main species                                         |
| [test_data/mix_tb_win]                     | A mykrobe mixed result with _M. tuberculosis_ as the main species                              |
| [test_data/mixed_tb_lineage]               | A mykrobe mixed result with TB as the main species, but with mixed lineage                     |
| [test_data/more_chelonae_tb_assembled]     | An _M. chelonae_ "win" by competitive mapping, but with enough TB reads to assemble a genome.  |
| [test_data/mykrobe_species_differentiates] |                                                                                                |
| [test_data/no_lineage_tb]                  | _M. tuberculosis_ "win" by competitive mapping, mykrobe does not return lineage.               |
| [test_data/no_mykrobe]                     | NTM for which `mykrobe` does not generate phylogenic data                                      |
| [test_data/ont_het_variant]                |                                                                                                |
| [test_data/ont_many_het]                   |                                                                                                |
| [test_data/septicum]                       | _M. septicum_ by competitive mapping, _M. absecessus_ by mykrobe, competitive mapping priority |
| [test_data/tb_no_aa_mutations]             |                                                                                                |
| [test_data/tb_null_calls]                  |                                                                                                |
| [test_data/SRR2097047]                     | Bacteria, but not mycobacteria                                                                 |
| [test_data/WTCHG_885333_73205296_1]        | _M. tuberculosis_                                                                              |

## Glossary & Definitions

| Page in Portal | Name in Portal                                | JSON Path                                                                                        | Origin                        | Notes                                                                                                                                                                                                                                                                         |
|----------------|-----------------------------------------------|--------------------------------------------------------------------------------------------------|-------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Sample Details | Pipeline Outcome                              | $['Pipeline Outcome']                                                                            | summarise.py                  | Derived from logic around the completion status of each pipeline stage. It provides user feedback on how far through analysis the pipeline got and the reason for this (for example insufficient reads)                                                                       |
| Sample Details | Organisms Identified: Human                   | $['Organism Identification']['Human Reads']                                                      | N/A                           | Should come from CLI data as all human reads get removed prior to pipeline completion. In reality always reports None at the moment on json and portal                                                                                                                        |
| Sample Details | Organisms Identified: Unclassified Reads      | $['Organism Identification']['Unclassified Reads']                                               | Gatekeeper                    | Unclassified reads from gatekeeper as identified by Kraken2. These reads could not be identified as belonging to a specific pathogen. As they may form part of a Mycobacterium species they will be included in subsequent analysis stages                                    |
| Sample Details | Organisms Identified: Non-Mycobacterium Reads | $['Organism Identification']['Non-Mycobacterium Bacteria Reads']                                 | Gatekeeper                    | Logic is applied to the output of gatekeeper in summarise.py. This calculates the difference between the number of bacterial reads and the mycobacterial reads. It therefore represents the number of bacterial reads which do not originate from Mycobacterium.              |
| Sample Details | Organisms Identified: Mycobacterium Reads     | $['Organism Identification']['Mycobacterium Reads']                                              | Gatekeeper                    | Mycobacterium reads from gatekeeper as identified by Kraken2                                                                                                                                                                                                                  |
| Sample Details | Mycobacterial Species Identified: Name        | $['Mycobacterium Results']['Summary']['Name']                                                    | Mykrobe / Competitive Mapping | Name, coverage and depth are taken from Mykrobe if a TB species is identified. For other Myco species results are derived from Competitive Mapping or Mykrobe depending on the species and coverage. Summarise.py amends and manipulates strings to generate final name shown |
| Sample Details | Mycobacterial Species Identified: Reads       | $['Mycobacterium Results']['Summary']['Num Reads']                                               | Mykrobe / Competitive Mapping | Reads is taken from Competitive mapping.                                                                                                                                                                                                                                      |
| Sample Details | Mycobacterial Species Identified: Coverage    | $['Mycobacterium Results']['Summary']['Coverage']                                                | Mykrobe / Competitive Mapping | Name, coverage and depth are taken from Mykrobe if a TB species is identified. For other Myco species results are derived from Competitive Mapping or Mykrobe depending on the species and coverage.                                                                          |
| Sample Details | Mycobacterial Species Identified: Depth       | $['Mycobacterium Results']['Summary']['Depth']                                                   | Mykrobe / Competitive Mapping | Name, coverage and depth are taken from Mykrobe if a TB species is identified. For other Myco species results are derived from Competitive Mapping or Mykrobe depending on the species and coverage.                                                                          |
| Sample Summary | Main Species                                  | $['Mycobacterium Results']['Species']['Name']                                                    | Competitive Mapping           | Species name is taken from Competitive Mapping results                                                                                                                                                                                                                        |
| Sample Summary | Total Reads (M)                               | $['Mycobacterium Results']['Species']['Num Reads']                                               | Competitive Mapping           | Species num reads is taken from Competitive Mapping results                                                                                                                                                                                                                   |
|                |                                               | $['Mycobacterium Results']['Species']['Coverage']                                                | Competitive Mapping           | Species Coverage is taken from Competitive Mapping results                                                                                                                                                                                                                    |
|                |                                               | $['Mycobacterium Results']['Species']['Mean Depth']                                              | Competitive Mapping           | Species Mean Depth is taken from Competitive Mapping results                                                                                                                                                                                                                  |
|                |                                               | $['Mycobacterium Results']['Species']['Length']                                                  | Competitive Mapping           | Species Length is taken from Competitive Mapping results                                                                                                                                                                                                                      |
|                |                                               | $['Mycobacterium Results']['Phylogenic Group']['Name']                                           | Mykrobe                       | Data extracted from Mykrobe results                                                                                                                                                                                                                                           |
|                |                                               | $['Mycobacterium Results']['Phylogenic Group']['Coverage']                                       | Mykrobe                       | Data extracted from Mykrobe results                                                                                                                                                                                                                                           |
|                |                                               | $['Mycobacterium Results']['Phylogenic Group']['Median Depth']                                   | Mykrobe                       | Data extracted from Mykrobe results                                                                                                                                                                                                                                           |
|                |                                               | $['Mycobacterium Results']['Subspecies']['Name']                                                 | Mykrobe                       | Data extracted from Mykrobe results                                                                                                                                                                                                                                           |
|                |                                               | $['Mycobacterium Results']['Subspecies']['Coverage']                                             | Mykrobe                       | Data extracted from Mykrobe results                                                                                                                                                                                                                                           |
|                |                                               | $['Mycobacterium Results']['Subspecies']['Median Depth']                                         | Mykrobe                       | Data extracted from Mykrobe results                                                                                                                                                                                                                                           |
|                |                                               | $['Mycobacterium Results']['Lineage']['Name']                                                    | Mykrobe                       | Data extracted from Mykrobe results                                                                                                                                                                                                                                           |
|                |                                               | $['Mycobacterium Results']['Lineage']['Coverage']                                                | Mykrobe                       | Data extracted from Mykrobe results                                                                                                                                                                                                                                           |
|                |                                               | $['Mycobacterium Results']['Lineage']['Median Depth']                                            | Mykrobe                       | Data extracted from Mykrobe results                                                                                                                                                                                                                                           |
|                |                                               | $['Genomes']['Name']                                                                             | summarise.py                  | Hardcoded value based on whether full pipeline analysis was completed                                                                                                                                                                                                         |
| Sample Details | Sequencing Quality: Mapped to                 | $['Genomes']['Sequencing Quality']['Mapped To']                                                  | Competitive Mapping           | rname value from competitive mapping                                                                                                                                                                                                                                          |
| Sample Details | Sequencing Quality: Reads                     | $['Genomes']['Sequencing Quality']['Num Reads']                                                  | Competitive Mapping           | Number of reads taken from competitive mapping                                                                                                                                                                                                                                |
| Sample Details | Sequencing Quality: Coverage                  | $['Genomes']['Sequencing Quality']['Coverage']                                                   | Clockwork/Sundial           | Proportion of bases which are called (so not N)                                                                                                                                                                                             |
| Sample Details | Sequencing Quality: Mean depth                | $['Genomes']['Sequencing Quality']['Mean Depth']                                                 | Competitive Mapping           | Mean Depth of reference mapping from Competitive Mapping                                                                                                                                                                                                                      |
| Sample Details | Sequencing Quality: Mixed calls               | $['Genomes']['Sequencing Quality']['Mixed Calls']                                                | Clockwork/Sundial                     | Clockwork/Sundial value for sequence quality mixed calls, denoting two variations of a gene at the same location having been identified                                                                                                                                               |
| Sample Summary | Resistance Prediction                         | $['Genomes']['Resistance Prediction']['Resistance Prediction Summary']                           | Gnomonicus                    | A condensed string representing the first and second line treatments is shown to the user in the portal. Derived from resistance prediction based on mutations identified and compared to the WHO catalogue.                                                                  |
| Sample Details | Resistance Prediction                         | $['Genomes']['Resistance Prediction']['Resistance Prediction Summary']                           | Gnomonicus                    | Full resistance prediction information shown to the user within sample details. Derived from resistance prediction based on mutations identified and compared to the WHO catalogue.                                                                                           |
| Sample Details | Relevant Mutations: Drug                      | $['Genomes']['Resistance Prediction']['Resistance Prediction Detail']['Drug Name']               | Gnomonicus                    | Three letter abbreviation of drug name                                                                                                                                                                                                                                        |
| Sample Details | Relevant Mutations: Gene                      | $['Genomes']['Resistance Prediction']['Resistance Prediction Detail']['Mutations']['Gene']       | Gnomonicus                    | Specific gene where mutation was identified                                                                                                                                                                                                                                   |
| Sample Details | Relevant Mutations: Mutation                  | $['Genomes']['Resistance Prediction']['Resistance Prediction Detail']['Mutations']['Mutation']   | Gnomonicus                    | Name of the mutation                                                                                                                                                                                                                                                          |
| Sample Details | Relevant Mutations: Nucleotide                | $['Genomes']['Resistance Prediction']['Resistance Prediction Detail']['Mutations']['Ref'/'Alt']  | Gnomonicus                    | Details of the mutated nucleotides                                                                                                                                                                                                                                            |
| Sample Details | Relevant Mutations: Coverage                  | $['Genomes']['Resistance Prediction']['Resistance Prediction Detail']['Mutations']['Coverage']   | Gnomonicus                    | Resistance prediction coverage a tuple where the first int is the number of reads supporting the wildtype (i.e. reference) base and the second int is the number of reads supporting the called mutation.                                                                     |
| Sample Details | Relevant Mutations: Prediction                | $['Genomes']['Resistance Prediction']['Resistance Prediction Detail']['Mutations']['Prediction'] | Gnomonicus                    | Resultant resistance prediction for the specific drug based upon this particular genetic mutation                                                                                                                                                                             |
| Sample Details | Relevant Mutations: Evidence                  | $['Genomes']['Resistance Prediction']['Resistance Prediction Detail']['Mutations']['Evidence']   | Gnomonicus                    | Not in use                                                                                                                                                                                                                                                                    |
