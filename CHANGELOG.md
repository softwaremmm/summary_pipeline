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
