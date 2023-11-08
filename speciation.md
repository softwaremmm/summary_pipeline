# Determination of mycobacterial species, subspecies and lineage by the Summary Pipeline 

Part of the Summary Pipeline works on genetic information that has already been assigned to the genus mycobacteriaceae. If the species is Mycobacterium tuberculosis then a lineage may also be assigned. Other species may be assigned a subspecies. This information forms part of the "Mycobacterium Results" section of the `main_report.json` file output by this repository e.g.

```json
"Mycobacterium Results": {
        "Summary": [
            {
                "Name": "M.abscessus_abscessus",
                "Num Reads": 92865,
                "Coverage": 64.768,
                "Depth": 3
            },
            {
                "Name": "M.tuberculosis (Unknown)",
                "Num Reads": 608,
                "Coverage": 1.35089,
                "Depth": 0.0166817
            }
        ],
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

Some of the information appears in the "Mycobacterial species identified" section of the user interface:

![M.tuberculosis](docs/mycobacterial_species_identified.png)

_Mycobacterium tuberculosis_ (Lineage 3)

![M.fortuitum_fortuitum](docs/subspecies.png)

_Mycobacterium fortuitum_ subspecies _fortuitum_

Two sources of information are used to inform the speciation decision [Competitive Mapping](https://github.com/GlobalPathogenAnalysisService/competitivemapping_pipeline) and [mykrobe](https://github.com/GlobalPathogenAnalysisService/lineagecalling_pipeline). These each output a JSON file which is analysed by the code in this repository to determine species information.  

Competitive Mapping outputs a list of species, which can be ordered by "coverage" (the proportion of a reference genome to which reads in the sample "map" i.e. are very similar to) to give a "top hit" species. However, Competitive Mapping does not provide information on lineage or subspecies. This information can in some cases be obtained from mykrobe, which reports subspecies, phylogenic group and lineage. 

Number of reads mapped (Reads) is always sourced from Competitive Mapping.

The way in which the Summary Pipeline assigns species, subspecies and lineage can be summarised by a graph. 

```mermaid
graph TD;
    MYKROBE_RETURN{{Has mykrobe returned any information?}};

    ALL_CM[Use name from Competitive Mapping.<br/>Use coverage and mean depth from Competitive Mapping.];

    TOPHIT_TB{{Is top hit M.tuberculosis?}};

    MYKROBE_SPECIES[Lookup name.<br/>Use coverage and median depth from mykrobe *species*.];

    TOPHIT_SPECIAL_NTM{{Is top hit in this list:<br/>M.intracellulare_chimaera,<br/>M.avium_hominissuis,<br/>M.paraintracellulare,<br/>M.intracellulare,<br/>M.lepraemurium,<br/>M.abscessus?}};

    MIXED{{Is there a mixed population?<br/>Mixed populations are defined as runs where myrkobe returns two phylo groups.}};

    PROCESS_SPECIAL_NTM_UNMIXED[Lookup name.<br/>Use coverage and median depth from mykrobe *lineage*.];

    LOW_COV{{Is coverage by competitive mapping less than 40%?}};

    MYKROBE_RETURN--Yes-->TOPHIT_TB;
    MYKROBE_RETURN--No-->ALL_CM;

    TOPHIT_TB--Yes-->MYKROBE_SPECIES;
    TOPHIT_TB--No-->TOPHIT_SPECIAL_NTM;

    TOPHIT_SPECIAL_NTM--Yes-->MIXED;
    MIXED--Yes-->ALL_CM;
    MIXED--No-->PROCESS_SPECIAL_NTM_UNMIXED;
    TOPHIT_SPECIAL_NTM--No-->LOW_COV;

    LOW_COV--Yes-->MYKROBE_SPECIES;
    LOW_COV--No-->ALL_CM;

```
_Determination of what species information to report_

The name returned is determined by using the species name from Competitive Mapping and the lineage name from mykrobe (if available). Where no combination of Competitive Mapping and lineage name can be found in the reference table ([example reference table](test_data/reference/name_mapping.csv)), the Competitive Mapping name is used.

## Additional steps for mixed populations

If _M. tuberculosis_ is not the "Main Species", _M. tuberculosis_ data from Competitive Mapping is appended to summary and species information, if any reads at all were mapped. If _M. tuberculosis_ is the "Main Species" in a mixed population, the information from the second hit from Competitive Mapping is appended to the summary information.