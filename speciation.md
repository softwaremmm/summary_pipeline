# Determination of mycobacterial species, subspecies and lineage naming by the Summary Pipeline 

Part of the Summary Pipeline works on genetic information that has already been assigned to the genus _mycobacteriaceae_. If the species is _Mycobacterium tuberculosis_ then a lineage may also be assigned. Species may be assigned a subspecies. This information forms the "Summary" part of the "Mycobacterium Results" section of the `main_report.json` file output by this repository e.g.

```json
"Mycobacterium Results": {
        "Summary": [
            {
                "Name": "M.abscessus_abscessus",
                "Num Reads": 92865,
                "Coverage": 76.639,
                "Depth": 2.4425
            },
            {
                "Name": "M.tuberculosis (Unknown)",
                "Num Reads": 608,
                "Coverage": 1.35089,
                "Depth": 0.0166817
            }
        ],
```

The remainder of the JSON data (e.g. "Phylogenic Group") is drawn from different sources...

```json
        "Species": [
            {
                "Name": "M.abscessus",
                "Num Reads": 92865,
                "Coverage": 76.639,
                "Mean Depth": 2.44258,
                "Length": 5067172.0
            },
            {
                "Name": "M.tuberculosis (Unknown)",
                "Num Reads": 608,
                "Coverage": 1.35089,
                "Mean Depth": 0.0166817,
                "Length": 4411532.0
            }
        ],
        "Phylogenic Group": [
            {
                "Name": "Non_tuberculosis_mycobacterium_complex",
                "Coverage": 71.839,
                "Median Depth": 3
            }
        ],
        "Subspecies": [
            {
                "Name": "Mycobacterium_abscessus",
                "Coverage": 71.839,
                "Median Depth": 3
            }
        ],
        "Lineage": [
            {
                "Name": "Mycobacterium_abscessus_subsp._abscessus",
                "Coverage": 64.768,
                "Median Depth": 3
            }
        ]
    },
```

Some of the information appears in the "Mycobacterial species identified" section of the user interface e.g.

![M.tuberculosis](docs/mycobacterial_species_identified.png)

_Mycobacterium tuberculosis_ (Lineage 3)

![M.fortuitum_fortuitum](docs/subspecies.png)

_Mycobacterium fortuitum_ subspecies _fortuitum_

The "**main species**" reported in the batch view is the first species in this list.

Two sources of information are used to inform the speciation decision: [Competitive Mapping](https://github.com/GlobalPathogenAnalysisService/competitivemapping_pipeline) and [mykrobe](https://github.com/GlobalPathogenAnalysisService/lineagecalling_pipeline). These each output a JSON file which is analysed by the code in this repository to determine species information.

Competitive Mapping outputs a list of species, which is ordered by "meandepth" (the mean number of reads mapped to an individual base in the reference genome) to give a "top hit" species. However, Competitive Mapping does not provide information on lineage or subspecies. This information can in some cases be obtained from mykrobe, which reports subspecies, phylogenic group and lineage. 

If the mycobacteria pipeline reaches a point where an _M. tuberculosis_ genome is assembled (and thus variants are called, relatedness and AMR information generated), _M. tuberculosis_ is always the main species (with lineage information appended, as appropriate).

In cases where mykrobe does not return any information, cases where competitive mapping returns a coverage of less than 40%, or cases where there is a **mixed population** containing an organism in this list (_M. intracellulare_chimaera_, _M. avium_hominissuis_, _M. paraintracellulare_, _M. intracellulare_, _M. lepraemurium_, _M. abscessus_) then the species name from Competitive Mapping is used. Otherwise, the name returned is looked up using the species name from Competitive Mapping and the lineage name from mykrobe (if available). Where no combination of Competitive Mapping and lineage name can be found in the reference table ([example reference table](test_data/reference/name_mapping.csv)), the Competitive Mapping name is used. 

Coverage, depth and number of reads mapped (Reads) are always sourced from Competitive Mapping.

## Additional steps for mixed populations

This software identifies a mixed population where mykrobe returns two phylo groups.

If _M. tuberculosis_ is not the "Main Species", _M. tuberculosis_ data from Competitive Mapping is appended to summary and species information, if any reads at all were mapped. If _M. tuberculosis_ is the "Main Species" in a mixed population, the information from the second hit from Competitive Mapping is appended to the summary information.

## Additional steps for mixed lineages

If more than one lineage of _M. tuberculosis_ is is returned, then species is reported as `M. tuberculosis (mixed lineage)`.