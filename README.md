# summary_pipeline

Summarises output from sub-workflows (part of WP8)

## Installation

1. Clone this repository
2. Create a conda environment `conda create -f -y -n summary_pipeline python=3.11`

## Usage

```{bash}
conda activate summary_pipeline
```

```{bash}
python summarise.py --gatekeeper test_data/example_input/2/gatekeeper_report.json --mapping test_data/example_input/2/competitivemapping_report.json --mykrobe test_data/example_input/2/mykrobe_report.json --gnomonicus test_data/example_input/2/tb/gnomonicus.json
```