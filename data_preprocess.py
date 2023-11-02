#!/usr/bin/env python
# coding: utf-8

# # Data pre-processing. Keister Zooplankton Hood Canal 2012-13 data
# 
# University of Washington Pelagic Hypoxia Hood Canal project, Zooplankton dataset.
# 
# 11/2, 10/31, 3/27-25,20 2023

from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np
import pandas as pd


def read_and_parse_sourcedata():
    """
    Read, parse and pre-process source csv data.
    """

    # ## Read the csv file

    data_pth = Path(".")
    sourcecsvdata_pth = data_pth / "sourcedata" / "bcodmo_dataset_682074_data.csv"
    source_df = pd.read_csv(sourcecsvdata_pth, skiprows=[1])


    # ## Fix time issues
    # 
    # - Assign correct timezone (PDT, not UTC)
    # - Fill in missing `time_start`, by `sample_code`
    missing_times = {
        "20131003DBDm1_200": "14:11",
        "20130904HPNm1_200": "21:59",
        "20130903UNDm1_335": "15:01",
        "20121001UNDm1_200": "14:12",
        "20120709UNNm5_335": "22:10",
        "20120709UNNm4_335": "22:45"
    }

    # Set the `time_start` strings for the `sample_code` entries in `missing_times`.
    for sample_code,time_start in missing_times.items():
        source_df.loc[source_df["sample_code"] == sample_code, "time_start"] = time_start

    # Create (replace) the `time` column based on `date`, `time_start`, my custom `pdt` timezone, and `strftime`
    pdt = timezone(timedelta(hours=-7), "PDT")
    source_df["time"] = pd.to_datetime(
        source_df["date"].astype(str) + source_df["time_start"], 
        format="%Y%m%d%H:%M"
    ).dt.tz_localize(pdt)


    # ## Replace incorrect life_history_stage values

    # - Simple replacement of "F1_0;_Furcilia_1_0_legs" entry with "F10;_Furcilia_10". Use pandas `replace` on the column
    # - EUPHAUSIA_PACIFICA and THYSANOESSA in `species` column: replace `life_history_stage` based on combined `species` and `life_history_stage` entries
    #   > Calyptopis 1-3 life_history_stage codes. For Euphasia Pacifica, calyptopis life stages are typically coded in life_history_stage as "Cal1;_Calyptopis_1", "Cal2;_Calyptopis_2" and "Cal3;_Calyptopis_3" (same for thysanoessa). But there are a few Euphasia records that include the following codes: "1;_CI", "2;_CII", "3;_CIII". These are the same life_history_stage codes used for copepods, copepodites C1 - C3. My guess is that they're miscoded and should be calyptopis 1-3. Can you confirm?
    # 
    #   Yes, these are miscoded ("1, CI" should be "Cal1, calyptopis 1," and so on).

    def _update_lhs_byspecies(species, lhs_updates):
        """Modifies source_df in place, within the function"""
        sel_species = source_df["species"].isin(species)
        for old_lhs,new_lhs in lhs_updates.items():
            source_df.loc[sel_species & source_df["life_history_stage"].str.startswith(old_lhs), "life_history_stage"] = new_lhs

    source_df["life_history_stage"].replace({"F1_0;_Furcilia_1_0_legs": "F10;_Furcilia_10"}, inplace=True)

    krill_bad_lhs = {
        "1;_CI": "Cal1;_Calyptopis_1", 
        "2;_CII": "Cal2;_Calyptopis_2",
        "3;_CIII": "Cal3;_Calyptopis_3",
    }
    _update_lhs_byspecies(["EUPHAUSIA_PACIFICA", "THYSANOESSA"], krill_bad_lhs)

    # Handle life stage correction SIPHONOPHORA corrections from Amanda
    siphonophora_bad_lhs = {
        "Medusa": "Nectophore", 
        "Unknown": "Nectophore",
    }
    _update_lhs_byspecies(["SIPHONOPHORA"], siphonophora_bad_lhs)


    # ## Perform updates to species (taxa), life_history_stage and density
    # Specific to certain sample_code entries, not across the board.
    # Focused on Jellyfishes, mites and one sinophora record
    
    # If the "new" lhs or density value in Amanda's spreadsheet is the same as the old one,
    # I've entered None rather than repeating the value, for clarity for intent.
    jellyfishes_mites_updates = [
        dict(old=("20120614DBDm2_200", "JELLYFISHES", "Medusa"), new=("HYDROZOA", None, None)),
        dict(old=("20120614DBDm4_200", "JELLYFISHES", "Unknown"), new=("HYDROZOA", "Medusa", None)),
        dict(old=("20120712DBDm4_200", "JELLYFISHES", "Medusa"), new=("CALYCOPHORAE", "Gonophore", None)),
        dict(old=("20120905DBDm4_200", "JELLYFISHES", "Medusa"), new=("HYDROZOA", None, None)),
        dict(old=("20120905DBNm3_200", "JELLYFISHES", "Unknown"), new=("CALYCOPHORAE", "Gonophore", None)),
        dict(old=("20120709UNDm3_200", "JELLYFISHES", "Medusa"), new=("CALYCOPHORAE", "Gonophore", None)),
        dict(old=("20130930UNDm3_200", "MITES", "4;_CIV"), new=("MICROCALANUS", None, None)),
        dict(old=("20120902UNiiNm1_200", "JELLYFISHES", "Medusa"), new=("HYDROZOA", None, None)),
        dict(old=("20120902UNiiNm4_200", "JELLYFISHES", "Medusa"), new=("CALYCOPHORAE", "Bract", 23.52941)),
        dict(old=("20121001UNNm3_200", "SIPHONOPHORA", "Nectophore"), new=("CALYCOPHORAE", "Gonophore", None)), 
        dict(old=("20121001UNNm3_200", "JELLYFISHES", "Medusa"), new=("HYDROZOA", None, None)),
    ]
    # For ("20121001UNNm3_200", "SIPHONOPHORA", "Nectophore"), I changed from the original Medusa lhs 
    # to Nectophore to account for the lhs change already executed in an earlier step.
    # For ("20120614DBDm4_200", "JELLYFISHES", "Unknown") and
    # ("20121001UNNm3_200", "JELLYFISHES", "Medusa"), replaced the assigned "HYDROZOA_Medusa" and 
    # "HYDROMEDUSA", respectively, to "HYDROZOA" b/c those two entries don't resolved with pyworms
    # (are not taxa names per se?)
    # I also ommitted SIPHONOPHORA	Nectophore from Amanda's spreadsheet because, unlike all other entries
    # in the "jellyfishes and mites" tab, the intent wasn't clear

    for upd_record in jellyfishes_mites_updates:
        old, new = upd_record["old"], upd_record["new"]
        # select on the entries from the "old" tuple forming a set of unique combinations of
        # sample_code, species and life_history_stage
        sel = (
            (source_df["sample_code"] == old[0])
             & (source_df["species"] == old[1])
             & (source_df["life_history_stage"] == old[2])
        )
        source_df.loc[sel, "species"] = new[0]
        if new[1] is not None:
            source_df.loc[sel, "life_history_stage"] = new[1]
        if new[2] is not None:
            source_df.loc[sel, "density"] = new[2]


    # ## Parse life_history_stage

    source_df[['lhs_0', 'lhs_1']] = pd.DataFrame(
        source_df.life_history_stage.str.split(';_').to_list(), 
        index=source_df.index
    )


    # ## Replace outdated/incorrect taxa with updated, corrected ones from Amanda

    taxa_corrections_updates = {
        "AETIDEUS_divergens": "AETIDEUS",
        "ANTHOMEDUSAE": "ANTHOATHECATA",
        "CALLIANASSA_CALIFORNIENSIS": "NEOTRYPAEA_CALIFORNIENSIS",
        "CANCER_ANTENNARIUS": "CANCRIDAE",
        "CANCER_PROD/OREG": "CANCRIDAE",
        "CORYCAEUS_ANGLICUS": "DITRICHOCORYCAEUS_ANGLICUS",
        "CLYTIA": "CLYTIA_GREGARIA",
        "EUCHAETA_ELONGATA": "PARAEUCHAETA_ELONGATA",
        "EUCHAETA": "PARAEUCHAETA ",
        "LEPTOMEDUSAE": "LEPTOTHECATA",
        "MICROCALANUS_PUSILLUS": "MICROCALANUS",
        "OITHONA_SPINIROSTRIS": "OITHONA_ATLANTICA",
        "ONCAEA_BOREALIS": "TRICONIA_BOREALIS",
        "PARACALANUS_PARVUS": "PARACALANUS",
        "PARATHEMISTO": "THEMISTO_PACIFICA",
        "PORCELAIN_CRABS": "PORCELLANIDAE",
    }
    source_df["species"].replace(taxa_corrections_updates, inplace=True)


    # ### Examine sample_code characteristics, extra characters

    # source_df.sample_code.str.len().value_counts()
    # source_df[source_df.sample_code.str.len().isin([14,19,20])].head()
    # source_df[source_df.sample_code.str.len() == 18].head()


    # ### Extract net_code and "extra token" from sample_code
    # 
    # - Retain only ones that are not already found among the existing dataframe columns.
    # - Example: "20120611UNDm2_200". Dataset description entry for 
    #   `sample_code`: "PI issued sample ID; sampling date + Station + D (day) or N (night) + Net code (e.g. m1) \_mesh"
    # - The upper case letter character before the "m" is D or N (Day or Night). **In a few cases there's an 
    #   additional character found before the D/N character, but its meaning is not described in the `sample_code` description**
    # - Ultimately, try to pull out or create a profile code and profile depth interval code, if appropriate?

    # Parsing steps:
    # - split the new `sample_code` on the "_" delimiter, create two new columns, `token1` and `mesh_size`
    # - From `token1` extract `token2`, the characters between `station_code` and the "_" delimiter
    # - parse `token2`: split on the letter "m", into `token3` and `net_code`; then create `token4` from `token3` by
    #   removing the D/N character. `token4` will be empty in most cases, and will be renamed to `extra_sample_token`

    def split_token2(token2):
        token3, net_code = token2.split('m')
        token4 = token3[:-1]

        return pd.Series({
            'net_code': 'm'+net_code,
            'extra_sample_token': token4
        })

    source_df['token2'] = source_df['sample_code'].apply(
        lambda cd: cd[10:].split('_')[0]
    )
    source_df = pd.concat([source_df, source_df['token2'].apply(split_token2)], 
                                axis='columns')
    source_df.drop(columns='token2', inplace=True)

    
    # ## Address "duplicate" records with different density values
    
    # Unique combinations of these three columns correspond to what should be a unique record.
    cols = ['sample_code', 'species', 'life_history_stage']

    # Identify the records that are duplicated, as the unique combination of `cols` columns. 
    # This is `duplicated_df`. `all_dups_source_df` then stores all the records matching 
    # these duplicated records (x2) but now adding the `density` column.
    duplicated_df = source_df[source_df[cols].duplicated()][cols]
    all_dups_source_df = source_df[cols + ['density']].merge(duplicated_df, on=cols, how="inner")

    # Calculate mean density for each pair of duplicated records.
    mean_density_df = all_dups_source_df.groupby(cols).mean().reset_index().rename(columns={"density":"density_avg"})

    # Merge the average-density dataframe with `source_df`. The net effect is to add a new column, `density_avg`
    source_meandensity_df = source_df.merge(mean_density_df, on=cols, how="left")

    #  The `sel` approach below is based on matching multi-indices in the two dataframes, using the 3-column `cols` set. 
    # (from https://stackoverflow.com/questions/54006298/select-rows-of-a-dataframe-based-on-another-dataframe-in-python)
    # For the 34 duplicated records only, assign `density_avg` to the `density` column. Then clean up: drop the 
    # `density_avg` column and, finally, drop what are now true duplicates (ie, 17 records). 
    # `source_final_df` is the final, de-duplicated, density-averaged dataframe.
    sel = source_meandensity_df.set_index(cols).index.isin(mean_density_df.set_index(cols).index)
    source_meandensity_df.loc[sel, 'density'] = source_meandensity_df[sel]['density_avg']

    source_final_df = source_meandensity_df.drop(columns=["density_avg"]).drop_duplicates()

    return source_final_df
