# Summary Pipeline

Summarises output from sub-workflows (part of WP8).

## Installation

1. Clone this repository
2. Create a conda environment `conda create -f -y -n summary_pipeline python=3.11`
3. Activate the conda environment e.g. `conda activate summary_pipeline`
4. Install this software `pip install .` (use `pip install -e .[dev]` for development)

## Usage

```{bash}
conda activate summary_pipeline
```

### Python (via CLI)

#### Specify individual report files

```{bash}
summary_json --gatekeeper test_data/WTCHG_885333_73205296_1/speciation_report.json --mapping test_data/WTCHG_885333_73205296_1/species_comparison_report.json --mykrobe test_data/WTCHG_885333_73205296_1/subspecies_report.json --gnomonicus test_data/WTCHG_885333_73205296_1/tb/resistance_prediction_report.json --knowledge test_data/WTCHG_885333_73205296_1/knowledge.json --versions test_data/WTCHG_885333_73205296_1/pipeline_versions.txt --clockwork test_data/WTCHG_885333_73205296_1/genome_creation_report.json --name_mapping test_data/reference/name_mapping.csv
```

All arguments are mandatory. This functionality is not used by the NextFlow pipeline and may be removed in future.

#### Pass report files as a list

```{bash}
summary_json --reports test_data/WTCHG_885333_73205296_1/pipeline_versions.txt test_data/WTCHG_885333_73205296_1/speciation_report.json test_data/WTCHG_885333_73205296_1/species_comparison_report.json test_data/WTCHG_885333_73205296_1/subspecies_report.json test_data/WTCHG_885333_73205296_1/tb/resistance_prediction_report.json test_data/WTCHG_885333_73205296_1/genome_creation_report.json test_data/WTCHG_885333_73205296_1/knowledge.json
```

### NextFlow

```{bash}
nextflow run . --reports ./test_data/WTCHG_885333_73205296_1/speciation_report.json,./test_data/WTCHG_885333_73205296_1/species_comparison_report.json,./test_data/WTCHG_885333_73205296_1/subspecies_report.json,./test_data/WTCHG_885333_73205296_1/tb/resistance_prediction_report.json
```

## Testing

### Running tests

Install for development and run `pytest`. No NextFlow tests are yet present.

### Test Data

Descriptions of test data.

| Test Data Directory | Description |
| --- | --- |
| ToDo | _????_, less than 40% coverage by competitive mapping |
| [test_data/002b5813-d1a3-4714-93ce-1075bfe6c7fe] | _M. abscessus_, more than 40% coverage by competitive mapping |
| [test_data/2f56a0f7-feb6-4994-8420-23adf5e2df46] | _M. malmoense_, more than 40% coverage by competitive mapping | 
| [test_data/clade_animal_A3] | _M. tuberculosis_ with lineage not specified as a number |
| [test_data/covid] | Covid |
| [test_data/covid_no_meta] | Covid but without a pipeline versions file |
| [test_data/mix_ntm_win] | A mykrobe mixed result with an NTM as the main species |
| [test_data/mix_tb_win] | A mykrobe mixed result with _M. tuberculosis_ as the main species |
| [test_data/SRR2097047] | Bacteria, but not mycobacteria |
| [test_data/no_mykrobe] | NTM for which `mykrobe` does not generate phylogenic data |
| [test_data/WTCHG_885333_73205296_1] | _M. tuberculosis_ |