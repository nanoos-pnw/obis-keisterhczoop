#!/usr/bin/env python
# coding: utf-8

# # Data pre-processing. Keister Zooplankton Hood Canal 2012-13 data
# 
# University of Washington Pelagic Hypoxia Hood Canal project, Zooplankton dataset.
# 
# 3/27-25,20 2023

from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np
import pandas as pd


def read_and_parse_sourcedata():
    data_pth = Path(".")

    # ## Pre-process data from csv for Event table

    # ### Read the csv file

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

    source_df["life_history_stage"].replace({"F1_0;_Furcilia_1_0_legs": "F10;_Furcilia_10"}, inplace=True)

    sel_species = source_df["species"].isin(["EUPHAUSIA_PACIFICA", "THYSANOESSA"])

    krill_bad_life_history_stages = {
        "1;_CI": "Cal1;_Calyptopis_1", 
        "2;_CII": "Cal2;_Calyptopis_2",
        "3;_CIII": "Cal3;_Calyptopis_3",
    }

    for old_lhs,new_lhs in krill_bad_life_history_stages.items():
        source_df.loc[sel_species & source_df["life_history_stage"].str.startswith(old_lhs), "life_history_stage"] = new_lhs


    # ## Parse `life_history_stage`

    source_df[['lhs_0', 'lhs_1']] = pd.DataFrame(
        source_df.life_history_stage.str.split(';_').to_list(), 
        index=source_df.index
    )


    # ### Examine sample_code characteristics, extra characters

    # source_df.sample_code.str.len().value_counts()
    # source_df[source_df.sample_code.str.len().isin([14,19,20])].head()
    # source_df[source_df.sample_code.str.len() == 18].head()


    # ### Extract net_code and "extra token" from `sample_code`
    # 
    # - Retain only ones that are not already found among the existing dataframe columns.
    # - Example: "20120611UNDm2_200". Dataset description entry for `sample_code`: "PI issued sample ID; sampling date + Station + D (day) or N (night) + Net code (e.g. m1) \_mesh"
    # - The upper case letter character before the "m" is D or N (Day or Night). **In a few cases there's an additional character found before the D/N character, but its meaning is not described in the `sample_code` description**
    # - Ultimately, try to pull out or create a profile code and profile depth interval code, if appropriate?

    # Parsing steps:
    # - split the new `sample_code` on the "_" delimiter, create two new columns, `token1` and `mesh_size`
    # - From `token1` extract `token2`, the characters between `station_code` and the "_" delimiter
    # - parse `token2`: split on the letter "m", into `token3` and `net_code`; then create `token4` from `token3` by removing the D/N character. `token4` will be empty in most cases, and will be renamed to `extra_sample_token`

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

    return source_df
