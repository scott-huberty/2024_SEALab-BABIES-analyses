from pathlib import Path

import pandas as pd
from scipy import stats

from . import paths


def get_gestational_age_df():
    """Read the CSV file containing the gestational age of the babies.
    
    Returns
    -------
    pd.DataFrame
        A DataFrame containing the gestational age of the babies for the newborn and
        sixmonth scans.
    """
    # this CSV File shared by Yanbin has computed gestational age in days, weeks, and months.
    fname_ages = paths.P_ROOT / "csv" / "babies_demo_updated_with_ages.csv"
    assert fname_ages.exists()
    df_ages = pd.read_csv(fname_ages)
    df_ages["study_id"] = df_ages["study_id"].apply(
        lambda study_id: "sub-" + str(study_id)
    )
    # subset the dataframe to relevant columns
    df_ages = df_ages[["study_id", "1mo_scan_age_wks", "6mo_scan_age_wks"]]
    new_names = {
        "1mo_scan_age_wks": "newborn_scan_age_weeks",
        "6mo_scan_age_wks": "sixmonth_scan_age_weeks",
    }
    df_ages = df_ages.rename(columns=new_names)
    return df_ages


def get_brainvol_df(fname, zscore=False):
    """Read the output of Freesurfer's aseg2stats into a Pandas DataFrame.

    Parameters
    ----------
    fname : pathlib.Path | str
        The path to the aseg2stats produced filename,
        e.g. `aseg_newborn_brainvol.table.txt`
    zscore : bool
        Whether to perform Z-score normalization on the Brain volume values.
        Defaults to False.

    Returns
    -------
    pd.DataFrame
        a Pandas DataFrame representation of the file.
    """
    df = pd.read_csv(fname, sep="\t")
    df = df.rename(columns={"Measure:volume": "study_id"})
    # split sub-????_ses-{newborn, sixmonth} on the underscore. extract the sub-??? part
    df["study_id"] = df["study_id"].str.split("_").str[0]

    id_col = ["study_id"]
    brain_cols = [
        "BrainSegVolNotVent",
        "SubCortGrayVol",
        "CortexVol",
        "TotalGrayVol",
        "CerebralWhiteMatterVol",
    ]
    use_cols = id_col + brain_cols

    if zscore:
        df[brain_cols] = df[brain_cols].apply(stats.zscore)

    df_long = df[use_cols].melt(
        id_vars=["study_id"],
        value_vars=use_cols,
        value_name="volume",
        var_name="region",
    )
    return df_long.set_index("study_id")


def get_aparc_long_format(fname):
    """Read either the lh.aparc.stats or rh.aparc.stats file into a long format DataFrame.

    Parameters
    ----------
    fname : str | pathlib.Path
        The path to the lh.aparc.stats or rh.aparc.stats file.
        For example ``aparc_newborn_lh.csv`` or ``aparc_newborn_rh.csv``.

    Returns
    -------
    pd.DataFrame
        A long format DataFrame containing the data from either hemisphere.

    Notes
    -----
    This function is designed to work with the
    ``aparc_{newborn, sixmonth}_{lh, rh}.csv`` files that typically reside in the
    ``csv`` directory of this project. If you don't have these files, you can generate
    them by running the scripts/get_freesurfer_stats.py script, but note that you need
    to be run this script on a computer that is mounted to the Lab server.

    Examples
    --------
    >>> fname = "aparc_newborn_lh.csv"
    >>> df = get_aparc_long_format(fname)
    """

    df = pd.read_csv(fname)
    return df.melt(
        id_vars=["study_id", "StructName"],
        var_name="metric",
    )


def get_aparc_all_hemisphere(fname_lh, fname_rh):
    """Read the csv file containing each subjects Freesurfer {lh,rh}.aparc.stats data.

    Parameters
    ----------
    fname_lh : str | pathlib.Path
        The path to the lh.aparc.stats file. For example ``aparc_newborn_lh.csv``.
    fname_rh : str | pathlib.Path
        The path to the rh.aparc.stats file. For example ``aparc_newborn_rh.csv``.

    Returns
    -------
    pd.DataFrame
        A long format DataFrame containing the data from both hemispheres.

    Notes
    -----
    This function is designed to work with the
    ``aparc_{newborn, sixmonth}_{lh, rh}.csv`` files that typically reside in the
    ``csv`` directory of this project. If you don't have these files, you can generate
    them by running the scripts/get_freesurfer_stats.py script, but note that you need
    to be run this script on a computer that is mounted to the Lab server.

    Examples
    --------
    >>> fname_lh = "aparc_newborn_lh.csv"
    >>> fname_rh = "aparc_newborn_rh.csv"
    >>> df_hemis = get_aparc_all_hemisphere(fname_lh, fname_rh)
    """
    df_lh = get_aparc_long_format(fname_lh)
    df_lh["hemisphere"] = "lh"
    df_lh["StructName"] = df_lh["StructName"].str.replace("lh-", "")
    df_rh = get_aparc_long_format(fname_rh)
    df_rh["hemisphere"] = "rh"
    df_rh["StructName"] = df_rh["StructName"].str.replace("rh-", "")
    df_hemis = pd.concat([df_lh, df_rh])
    return df_hemis
