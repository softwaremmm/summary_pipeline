# summary_pipeline

Summarises output from sub-workflows (part of WP8)

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
summary_json --gatekeeper test_data/example_input/WTCHG_885333_73225298_1/2/gatekeeper_report.json --mapping test_data/example_input/WTCHG_885333_73225298_1/2/competitivemapping_report.json --mykrobe test_data/example_input/WTCHG_885333_73225298_1/2/mykrobe_report.json --gnomonicus test_data/example_input/WTCHG_885333_73225298_1/2/tb/gnomonicus.json
```

#### Pass report files as a list

```{bash}
summary_json --reports test_data/example_input/WTCHG_885333_73225298_1/2/gatekeeper_report.json test_data/example_input/WTCHG_885333_73225298_1/2/competitivemapping_report.json test_data/example_input/WTCHG_885333_73225298_1/2/mykrobe_report.json test_data/example_input/WTCHG_885333_73225298_1/2/tb/gnomonicus.json
```

### NextFlow

```{bash}
nextflow run . --gatekeeper_report_path ./test_data/example_input/WTCHG_885333_73225298_1/2/gatekeeper_report.json --mapping_report_path ./test_data/example_input/WTCHG_885333_73225298_1/2/competitivemapping_report.json --mykrobe_report_path ./test_data/example_input/WTCHG_885333_73225298_1/2/mykrobe_report.json --gnomonicus_report_path ./test_data/example_input/WTCHG_885333_73225298_1/2/tb/gnomonicus.json
```