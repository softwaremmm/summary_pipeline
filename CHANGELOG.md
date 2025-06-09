## New
* Passthrough `Complex` for coverage of complex VCF rows which did not have evidence given due to complexity


## 2.5.0

Changes for nextflow linting and better local running

### Fix

- use tuples for channels
- rename test container param to be specific
- enable use of a glob for providing input reports (for local use)
- Correctly report mykrobe depth and coverage against lineage

### Chores

- Adopt Nextflow linting via Nextflow language server
- Remove redundant lines for error report and DSL2
- add publish_dir option
- add nf-test config

## 2.4.7 (2024-12-06)

### Fix

- strip whitespace from pipeline build

## 2.4.6 (2024-11-11)

### Fix

- remove debug and useless logging

## 2.4.5 (2024-11-05)

### Fix

- use get for dict
- add pytest just for naming
- use defaults instead of errors
- add missing mykrobe species which are in manifest
- use get for phylo_group
- add check for future M.tb lineages
- simplify naming in order to report mixed subspecies

## 2.4.4 (2024-11-01)

### Fix

- expand mapping csv and add generic lineage case

## 2.4.3 (2024-09-26)

### Fix

- Capture TB complex, unknown lineage in lookup
- Correctly report canettii

## 2.4.2 (2024-07-25)

### Fix

- update expectation for new name mapping
- Include M. avium in species list

## 2.4.1 (2024-07-25)

### Fix

- simplify naming system

## 2.4.0 (2024-07-16)

### Feat

- also push to gpasltd

## 2.3.4 (2024-07-12)

### Fix

- force TB win if genome assembled

## 2.3.3 (2024-07-12)

### Fix

- sort comp map by meandepth

## 2.3.2 (2024-07-02)

### Fix

- Correct spacing (mixed lineage)

## 2.3.1 (2024-06-27)

### Fix

- update format on species comparison report

## 2.3.0 (2024-06-26)

### Feat

- use full reference name for TB

### Refactor

- rename reference genome

## 2.2.10 (2024-06-25)

### Fix

- return only a single mutation for >1 snp in a codon

## 2.2.9 (2024-06-24)

### Fix

- formatting
- parse cov at null sites better

## 2.2.8 (2024-06-21)

### Fix

- Pipeline outcome messages

## 2.2.7 (2024-06-20)

### Fix

- correct readme seq quality descriptions
- rename clockwork to creation report

## 2.2.6 (2024-06-07)

### Fix

- allow gnomonicus reports to not specify ref/alt fields in mutations (happens if there are 0 AA mutations)
- progress

## 2.2.5 (2024-04-30)

### Fix

- use np nan
- set dtype when reading cov

## 2.2.4 (2024-04-26)

### Fix

- check coverage alt as well
- check for None type in coverage

## 2.2.3 (2024-04-04)

### Fix

- cleanup pandas print options
- ensure epistasis rules aren't filtered out when filtering for mutations with no effect

## 2.2.2 (2024-03-18)

### Fix

- allow null VCF idx

## 2.2.1 (2024-02-13)

### Fix

- enable BDQ in antibiogram for WHO v2 results

## 2.2.0 (2024-01-16)

### Feat

- commitizen bump triggers build and release

### Fix

- remove quotes
- hook for conventional commits

## 2.1.1 (2024-01-08)

### Fix

- corrects use of reports_list and reports params

## 2.1.0 (2024-01-08)

## 1.12.4 (2024-01-05)
A mix up resulted in this tag being created/added to changelog later than in should.
But merges should be pre 2.0.0

### Feat

- Always use competitive mapping coverage in summary

### Fix

- Summary depth from comp map only

## 2.0.1 (2024-01-05)

### Fix

- Include null calls and ref genome length in main report

### Refactor

- change mismatched and confusing test file names

## v2.0.0 (2023-12-15)

### Fix

- remove integration action

### Refactor

- Use PIPELINE_BUILD file

## 1.12.3 (2023-11-15)

### Fix

- Report mixed lineages as such

## 1.12.2 (2023-11-08)

### Fix

- Include TB when no mykrobe results returned

## 1.12.1 (2023-11-08)

### Fix

- Handle alternate mykrobe species

## 1.12.0 (2023-11-07)

### Feat

- Use lookup table for species naming
- Name mapping a mandatory input

## 1.11.1 (2023-10-31)

### Fix

- ensure `summary_name` is always populated

## 1.11.0 (2023-10-31)

### Feat

- Added pod labels to processes

## 1.10.1 (2023-10-30)

### Fix

- mean to median as approproriate
- Updating for changes to summary json format
- Updating following PR
- Updating reads origin
- correcting typo and adding resistance prediction coverage definition.
- Adding glossary to README.md for terminology in main_report.json and showing where used in the portal.

## 1.10.0 (2023-10-27)

### Feat

- Handles mixed pops
- Support name mapping file in CLI
- Treat phylo and mykrobe species as lists

### Fix

- Throw error with >2 speices in mix
- Remove name mapping, not currently needed
- Return reads when no mykrobe data
- Handle BCG
- Handle most cases
- Merge glitch
- Merge glitch

## 1.9.0 (2023-10-27)

### Feat

- Handle phylo and "subspecies" as lists

## 1.8.1 (2023-10-23)

### Fix

- Use lineage information for NTMs

## 1.8.0 (2023-10-20)

### Feat

- Num Reads in species summary

## 1.7.0 (2023-10-19)

### Feat

- Always include TB in species list (if present)

### Fix

- Also include TB in summary

## 1.6.1 (2023-10-18)

### Fix

- Handle empty mykrobe phylo/species/lineage output

## 1.6.0 (2023-10-17)

### Feat

- Logic for sub 40 CM coverage
- Allow no lineage
- Use competitive mapping, if not mykrobe
- Update speciation logic for TB

### Fix

- Use subspecies coverage for mykrobe

## 1.5.0 (2023-10-10)

### Feat

- Use genome_name, not #rname for "mapped to"

## 1.4.1 (2023-10-05)

### Fix

- Correctly assign knowledge

## 1.4.0 (2023-10-03)

### Feat

- Include reference filenames in main report
- CLI args for knowledge

## 1.3.2 (2023-09-25)

### Fix

- Handle mykrobe output with no species

## 1.3.1 (2023-09-25)

### Fix

- ensure functionality if no variants

## 1.3.0 (2023-09-21)

### Feat

- Include version info in report
- Update cli to support pipeline version info

### Fix

- Remove redundant list

## 1.2.2 (2023-09-15)

### Fix

- Ensure gene->null when `NaN`

## 1.2.1 (2023-09-08)

### Fix

- Ensure that None values are not parsed to int incorrectly

## 1.2.0 (2023-09-06)

### Feat

- Report pipeline outcome

## 1.1.7 (2023-09-05)

### Fix

- zero cov for TB and pick up MAC

## 1.1.6 (2023-09-04)

### Fix

- **docker**: fix docker.yaml latest tag

## 1.1.5 (2023-09-04)

### Fix

- **skip**: remove skip from commitizen message

## 1.1.4 (2023-09-04)

### Fix

- **docker-action**: update docker release action

## 1.1.3 (2023-09-04)

### Fix

- **README**: update README

## 1.1.2 (2023-09-04)

### Feat

- **commitizen**: add automated versioning

## v1.1.2 (2023-08-29)

## v1.1.1 (2023-08-25)

## v1.0.3 (2023-08-25)

## v1.0.2 (2023-08-16)

## v1.0.1 (2023-08-16)

## v1.0.0 (2023-08-15)

## v0.2.4 (2023-08-14)

## v0.2.2 (2023-08-08)

## v0.2.1 (2023-08-08)

## v0.2.0 (2023-08-03)

## 0.1.0 (2023-07-26)
