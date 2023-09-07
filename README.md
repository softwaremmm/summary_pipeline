# Summary Pipeline

Summarises output from sub-workflows (part of WP8).

## Installation

1. Clone this repository
2. Create a conda environment `conda create -f -y -n summary_pipeline python=3.11`
3. Activate the conda environment e.g. `conda activate summary_pipeline`
4. Install this software `pip install .` (use `pip install -e .` for development)

## Usage

```{bash}
conda activate summary_pipeline
```

### Python (via CLI)

#### Specify individual report files

```{bash}
summary_json --gatekeeper test_data/WTCHG_885333_73205296_1/speciation_report.json --mapping test_data/WTCHG_885333_73205296_1/species_comparison_report.json --mykrobe test_data/WTCHG_885333_73205296_1/subspecies_report.json --gnomonicus test_data/WTCHG_885333_73205296_1/tb/resistance_prediction_report.json
```

#### Pass report files as a list

```{bash}
summary_json --reports test_data/WTCHG_885333_73205296_1/pipeline_versions.txt test_data/WTCHG_885333_73205296_1/speciation_report.json test_data/WTCHG_885333_73205296_1/species_comparison_report.json test_data/WTCHG_885333_73205296_1/subspecies_report.json test_data/WTCHG_885333_73205296_1/tb/resistance_prediction_report.json test_data/WTCHG_885333_73205296_1/genome_creation_report.json
```

### NextFlow

```{bash}
nextflow run . --reports ./test_data/WTCHG_885333_73205296_1/speciation_report.json,./test_data/WTCHG_885333_73205296_1/species_comparison_report.json,./test_data/WTCHG_885333_73205296_1/subspecies_report.json,./test_data/WTCHG_885333_73205296_1/tb/resistance_prediction_report.json
```
