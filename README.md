# README

2024-02-29

This repository contains all the elements involved in the transformation of a Puget Sound zooplankton data from its original format to the standardized format used for integration into the [Ocean Biodiversity Information System (OBIS)](https://obis.org). Collection and analysis of the dataset ("Zooplankton densities collected from a seasonally hypoxic fjord on R/V Clifford A Barnes cruises from 2012-2013 (Pelagic Hypoxia project)") was led by the Principal Investigator, Julie Keister, [ORCID 0000-0002-9385-5889](https://orcid.org/0000-0002-9385-5889), University of Washington / NOAA. This dataset was previously published on [BCO-DMO](https://www.bco-dmo.org) in a format that was minimally changed from the format submitted by the PI.

The goal of the project captured in this repository was to transform this dataset into the [Darwin Core (DwC) standard format](https://ioos.github.io/bio_data_guide/intro.html) for submission to OBIS. This processing workflow starts with the reorganization and reformatting ("alignment") of a dataset's data to *DwC - [Event Core](https://manual.obis.org/formatting.html#when-to-use-event-core) with [Extended Measurement or Fact (eMoF) extension](https://manual.obis.org/data_format.html#obis-holds-more-than-just-species-occurrences-the-env-data-approach)* (also known as OBIS-ENV-DATA), the data standard used by OBIS.

The aligned dataset was first published on OBIS in January 2024 and may be browsed and accessed at https://obis.org/dataset/5463caa4-b929-477f-ae6c-7007b6d91baa. 

The alignment work was supported by the [Northwest Association of Networked Ocean Observing Systems (NANOOS)](https://www.nanoos.org), the Regional Association of the national [US Integrated Ocean Observing System (IOOS)](https://ioos.noaa.gov) for the US Pacific Northwest. It was carried out by Emilio Mayorga, [ORCID 0000-0003-2574-4623](https://orcid.org/0000-0003-2574-4623), University of Washington.


## Dataset description

This zooplankton dataset was collected as part of a larger study examining the effects of hypoxia on species composition, distributions, and predator-prey interactions between zooplankton and fish in a pelagic marine ecosystem. Day/night paired zooplankton sampling was conducted in Hood Canal, Puget Sound (Washington state, US), during 10 monthly cruises from June to October, 2012 and 2013, at five stations: Dabob, Union, Hoodsport, Duckabush and Twanoh. An obliquely towed multi-net system was used to collect depth stratified and full water column samples. For the depth-stratified sampling, depth layers were based on the dissolved oxygen profiles from CTD casts. In the laboratory, zooplankton were quantitatively subsampled and microscopically counted, with zooplankton densities calculated. All individuals were identified to species or larger taxonomic grouping, and by life stages for some species, within each sample. This dataset as published with OBIS incorporates corrections and updates to a dataset previously published on BCO-DMO.

**OBIS Dataset citation:** Keister J E, Essington T, Horne J K, Parker-Stetter S, Herrmann B, Li L, Mayorga E, Winans A (2024). Zooplankton densities collected from a seasonally hypoxic fjord (Hood Canal, Salish Sea, USA) on 2012-2013 cruises. Version 1.2. United States Geological Survey. Samplingevent dataset. https://doi.org/10.15468/a7upu6


## Data alignment

The starting point data file for OBIS Darwin Core alignment was obtained from a previous data submission to BCO-DMO available at [doi:10.1575/1912/bco-dmo.682074.1](https://doi.org/10.1575/1912/bco-dmo.682074.1). After downloading the file in CSV format from the [BCO-DMO ERDDAP server](https://erddap.bco-dmo.org/erddap/tabledap/bcodmo_dataset_682074.csv), we performed the following revisions and corrections, based on more recent information from the PI's lab:
- Assigned the correct timezone: PDT (local time, UTC-7), rather than UTC. 
- Populated missing times for 6 sampling events. 
- Corrected multiple life history stage entries. 
- Updated or corrected several taxa assignments. 
- Corrected a zooplankton density value. 
- Identified duplicate entries where only the zooplankton density values differed. In such cases, reduced the duplicates to single entries (17) with the mean density from the duplicate pairs.

These steps and data alignments work was implemented in Python code. See [`notebooks-notes.md`](notebooks-notes.md) for details.

### Dataset and project at BCO-DMO
- BCO-DMO Dataset 682074: [Zooplankton densities collected from a seasonally hypoxic fjord on R/V Clifford A Barnes cruises from 2012-2013 (Pelagic Hypoxia project)](https://www.bco-dmo.org/dataset/682074). Access from ERDDAP server [here](https://erddap.bco-dmo.org/erddap/tabledap/bcodmo_dataset_682074.html)
- This dataset is part of BCO-DMO Project 557504: [Consequences of hypoxia on food web linkages in a pelagic marine ecosystem (PelagicHypoxia)](https://www.bco-dmo.org/project/557504)


## Funding

The scientific study was funded by the NSF Division of Ocean Sciences, Award Number OCE-1154648. The transformation and publication of this dataset in OBIS was supported by the [Northwest Association of Networked Ocean Observing Systems (NANOOS)](https://www.nanoos.org).


## Bibliography

- Li, L., J.E. Keister, T.E. Essington and J. Newton. 2019. Vertical distributions and abundances of life stages of the euphausiid Euphausia pacifica in relation to oxygen and temperature in a seasonally hypoxic fjord. Journal of Plankton Research 41(2): 188–202, [doi:10.1093/plankt/fbz009](https://doi.org/10.1093/plankt/fbz009)
- Moriarty, P. E., T. E. Essington, J. K. J. E. Horne, Keister, L. Li, S. L. Parker-Stetter, and M. Sato. 2020. Unexpected food web responses to low dissolved oxygen in an estuarine fjord. Ecological Applications 30(8):e02204. [doi:10.1002/eap.2204](https://doi.org/10.1002/eap.2204)
