# Data processing code

5/4/2023. Emilio Mayorga

## Summary of the aligned files and processing code

We use Python code consisting of one module and four Jupyter notebooks to transform the source data CSV file to three CSV files "aligned" to the Darwin Core (DwC) extended Measurement or Fact (eMoF) standard. The source data file downloaded from BCO-DMO is called `bcodmo_dataset_682074_data.csv` and is found in the `sourcedata` directory.

### DwC eMoF aligned CSV files

The resulting DwC eMoF files are found in the `aligned_csvs` directory:

- `DwC_event.csv`: Event file. Each row defines a sampling "event", where each event is described with the event type (under `eventRemarks`), temporal and spatial information (including depth), a unique ID, and its relationship to a "parent" event if applicable. Three event types are defined: "cruise", "stationVisit" (with a cruise parent) and "sample" (with a stationVisit parent). A sample event is the sample collection from each net deployment, where the `eventID` is taken directly from the `sample_code` column in the original data file and a `samplingProtocol` description is included. 
  - There are 10 cruises, 64 station visits and 271 samples.
- `DwC_occurrence.csv`: Occurrence file. Each row defines a unique taxonomic identification and associated sex and life stage determinations, if present. Each occurrence entry is associated with a "sample" event in `DwC_event.csv` via the `eventID` code. The taxonomic description includes the associated taxonomic match up and details from WoRMS (World Register of Marine Species) based on the `species` column in the original data file, plus 10 manual matchups when an automatic matchup could not be made.
  - There are 6867 occurrences.
- `DwC_emof.csv`: eMoF file. The eMoF file provides a flexible and open-ended mechanism for storing additional information about the dataset not found in the Event and Occurrence files, or to provide additional details about information provided in those two files. Each eMoF type is associated with an external community vocabulary references specifying the measurement type and, when appropriate, the measurement unit. Currently 4 eMoF types are included:
  - density measurements: 6897 entries
  - multinet sampling descriptions: 271 entries
  - Sampling method descriptions: 271 entries
  - Sampling net mesh size descriptions: 271 entries

### Intermediate WoRMS taxonomic match-up file

The processing code creates two intermediate files that are not part of the final DwC-aligned output files: `intermediate_DwC_occurrence_life_history_stage.csv` and `intermediate_DwC_taxonomy.csv`. They are used as temporary information passed from one Jupyter notebook to another, or within the same notebook.

`intermediate_DwC_taxonomy.csv` contains the taxonomic match-up between the original `species` entry and the corresponding, fully fleshed out WoRMS information.

### Processing code

The processing code consists of a Python module file and four Python Jupyter notebooks.

- `data_preprocess.py`. This module serves as "pre-processor" and is called by each Jupyter notebook.  It reads the BCO-DMO source data file and applies several corrections and parsing steps: insert missing times for 6 samples; interpret timestamps as PDT; correct four `life_history_stage` entry errors (each error may occur in multiple samples); and parse the `life_history_stage` and `sample_code` entries into component strings for further processing.
- `Keister-dwcEvent.ipynb`. This notebook produces the `DwC_event.csv` file.
- `Keister-dwcTaxonomy.ipynb`. This notebook produces an intermediate file,  `intermediate_DwC_taxonomy.csv`, used later in the `Keister-dwcOccurrence.ipynb` notebook.
- `Keister-dwcOccurrence.ipynb`. This notebook produces the `DwC_occurrence.csv` file.
- `Keister-dwceMoF.ipynb`. This notebook produces the `DwC_emof.csv` file.

The processing code runs in a `conda` Python environment that can be created with the conda environment file `environment-py.yaml`. 

## Additional notes about each code file

The text below is largely cut and pasted from what used to be long introductory notes in each notebook.

### 0. data_preprocess.py

Note that the Jupyter notebook `data-preprocess.ipynb` contains effectively the same code. The notebook is used only to explore and document results of the data pre-processing steps. Only the module `data_preprocess.py` is used in the processing sequence.

### 1. Keister-dwcEvent.ipynb

Parse the data to define and pull out 3 event "types": `cruise`, `stationVisit` and `sample`. The DwC event table will be populated sequentially for each of those event types, in that order, from the most temporally aggregated (cruise) to the most granular (sample). Columns will be populated differently depending on the event type. Since a cruise is a spatial collection of points, a `footprintWKT` polygon and depth ranges are generated and populated.

**Notes about fields to use**
- mention why I'm not using `id` columns (see Abby's comments)
- consider adding `basisOfRecord`
- See additional fields used in the LifeWatch dataset: modified, language, rightsHolder, accessRights, institutionCode, datasetName, country (in addition to id, type, eventID, parentEventID, samplingProtocol, eventDate, locationID, waterBody, countryCode, minimumDepthInMeters, maximumDepthInMeters, decimalLatitude, decimalLongitude)

**date-time issues**
- Are times in UTC (as claimed by the `time` variable) or PDT?? Based on `day_night`, I think they're actually in PDT, not UTC!
- Inconsistencies between `time_start` and `day_night`. I've spotted at least one: sample ("20120611UNDm3_200") labelled as "Day" while `time_start` is "23:10". Clearly one of them is wrong. Test for other obvious inconsistencies by setting a time window for Day vs Night and comparing it to `time_start`.
- Missing `time_start` values. There are a few such cases, but apparently no corresponding missing `date` values. Still, they lead to `NaT` `time` values. I need to replace the `NaT`'s with a valid datetime, and the only option is to use the `date` and an artificial time value. Start with a fixed value (12:00), then refine it by using 12:00 when `day_night` is `Day` and 23:00 when it's `Night`.
- Times capture only the *start* of the sampling event. So, using times as the event end in an interval range would be misleading.

**Other comments**
- Add "Day sampling" / "Night sampling" to `eventRemarks` for sample events (or stationVisit, or both?), based on `day_night` column
- Parsing `sample_code` for distinctive information
  - Example `sample_code`: "20120611UNDm2_200". Dataset description entry for `sample_code`: "PI issued sample ID; sampling date + Station + D (day) or N (night) + Net code (e.g. m1) \_mesh"
  - The upper case letter character before the "m" is D or N (Day or Night). **In a few cases there's an additional character found before the D/N character, but its meaning is not described in the `sample_code` description**
- These were monthly cruises lasting about 4 days, in June-October 2012 and 2013 (ie, 8 cruises).
- DONE. Look up US `countryCode`

### 2. Keister-dwcTaxonomy.ipynb

- Refer to https://obis.org/manual/darwincore/#occurrence and https://obis.org/manual/darwincore/#taxonomy for guidance
- I won't use `acceptedname` and `acceptedNameID`; they are not needed or even recommended

Occurrence, identification and taxons. I had these questions for the Standardizing Marine Bio Data group:
- A number of the occurrences are at the "Class" (or higher) `taxonRank` level. Should these be included and submitted to OBIS/MBON?
- There are cases where there are is an occurrence at a "Genus" `taxonRank` and a separate occurrence in the same `eventID` but at a higher `taxonRank` ("Class"), for the same "Class". Should we still submit the higher-rank occurrence? For a specific example, see `eventID` "20120611UNDm1_200", with `scientificName` "Gastropoda" vs "Limacina helicina". Some of the higher-rank occurrences may involve younger life stages that are less easily resolved

Abby's response:
- Well it could be that the class rank is for a different organism that they were not able to identify down to a lower level as they were with the organism that they could. So in your example they are able to identify one organism to Limacina helicina but possibly the other Gastropoda is a completely different Order or Family than the Limacina helicina observation. Maybe it's in Tectibranchiata but they can't be sure. Long winded way to say yes keep both.
- Yes, keep everything. We never know what someone might be able to do with the data we're sharing so it's always best to keep all of it unless we find errors that we can confirm with the data provider and they want to remove those.

### 3. Keister-dwcOccurrence.ipynb

- Refer to https://obis.org/manual/darwincore/#occurrence and https://obis.org/manual/darwincore/#taxonomy for guidance
- `acceptedname` and `acceptedNameID` are not needed or even recommended


**TODO**

- Decide how to handle "absent" `occurrenceStatus`. Will need to decide when to assign "absent" occurrence, and how. From Li et al 2019, it's clear that for *Euphausia pacifica*, if there is no occurrence record for a "sample" (a specific net tow), "absence" is implied and can/should be entered. But how about others? Will have to consult with Julie and the Standardizing Bio data group

**Questions, issues, comments about life history and sex parsing**

- `life_history_stage` is exported in a separate, intermediate csv table together with `occurrenceID` in order to enable the join/merge needed for generating abundance measurements in emof.
- `life_stage_mappings` dictionary is now stored in an external JSON file
- Now that I've thoroughly compared `lhs_0` and `lhs_1`, it's clear that `lhs_1` can be thrown out. `lhs_0` is all that's needed
- `Female` and `Male` are only found for `Adult`, and only found in `lhs_0`
- Are `CI` - `CV` (and matching 1-5) the same as `Copepodite` 1 - 5? If they were, their use with *Euphausia Pacifica* (see the next cell) would be wrong. 
- Life stages `Calyptopis` 1-3, `Furcilia` 1-10 and `Zoea` 1-5 are not found in https://vocab.nerc.ac.uk/collection/S11/current/. That vocab doesn't have any "phases" for `Calyptopis`, `Furcilia` and `Zoea`
- These are also not found: `Bract`, `Gonophore`, `Nectophore`, `Polyp`
- `Furcilia_1_0_legs` is not clear

### 4. Keister-dwceMoF.ipynb

eMoF: Extended Measurement or Fact

**TODO:**

- See note after cell 34: **TODO/NOTE:** (updated on 5/4/2023)`len(emofsource_samplesoccur_df)`is 30 greater than the 6867 occurrences found in `dwcoccurrence_df`. Will need to investigate.
- DONE. Need to carry out a manual validation of the resulting emof table, specially for abundance. I'm seeing some repeated adjacent abundance values that are suspicious
- consider other eMoF's to include? eg: day vs night, and other event-level metadata
- **consider rounding off abundance values to, say, 2-3 significant digits after decimal point**
- sex and life stage from `life_history_stage`
    - Add emof records here, in addition to the `sex` and `lifeStage` columns added to the occurrence table?
    - sex vocabulary: http://vocab.nerc.ac.uk/collection/S10/current/
    - life stage vocabulary: http://vocab.nerc.ac.uk/collection/S11/current/
