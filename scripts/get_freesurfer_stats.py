import argparse

import os
import subprocess

from pathlib import Path

import pandas as pd

PROJECT_PATH = Path("/Volumes/HumphreysLab/Daily_2/BABIES/MRI").resolve()

def run_aseg2stats(session):
    """"Run Freesurfer asegstats2table command to generate brain volume stats for dataset.
    
    Parameters
    ----------
    session : str
        Must be either "newborn" or "sixmonth".

    Returns
    -------
    exit code : None
        Returns ``None``. If Succesful, a text file will be saved to
        `aseg_{session}_{metric}.table.txt` in the same directory as this script.
    
    Notes
    -----
    See: https://surfer.nmr.mgh.harvard.edu/fswiki/asegstats2table
    """
    ses_dir = "six_month" if session == "sixmonth" else session
    dpath = PROJECT_PATH / f"{ses_dir}/derivatives/Nibabies_auto/sourcedata/freesurfer"
    os.environ["SUBJECTS_DIR"] = str(dpath)

    this_dir = (Path(__file__).parent).resolve()

    fpath_sublist = this_dir / f"dec_{session}.table.dat"
    out_fpath = this_dir / f"aseg_{session}.table.txt"
    stats_fname = "brainvol.stats"
    
    command = [
        "asegstats2table",
        "--qdec",
        str(fpath_sublist),
        "--stats",
        stats_fname,
        "--tablefile",
        str(out_fpath),
    ]
    subprocess.run(command)

    # Now let's build our own DataFrame of volume metrics per Subject
    stats_paths = list(dpath.rglob(f"sub-*/stats/brainvol.stats"))
    dfs = []
    for stat_path in stats_paths:
        print(".", end="")
        # find the part of the path that contains sub-{id}_session-{session}
        study_id = [part for part in stat_path.parts if part.startswith("sub-")]
        assert len(study_id) == 1
        # get the str from the list
        study_id = study_id[0]
        # split the sub-{id}_ses-{session} string at the underscore
        study_id = study_id.split("_", maxsplit=1)
        assert study_id
        study_id = study_id[0]
        assert study_id.startswith("sub")
        # read the file into pandas
        df = pd.read_csv(stat_path)
        df["study_id"] = study_id
        dfs.append(df)
    # now create one DataFrame
    df_dataset = pd.concat(dfs, axis=0).set_index("study_id")
    df_dataset.to_csv(this_dir / f"brianvol_{session}.csv")
    return



def get_aparcstats(session, *, hemisphere):
    """"Get each subjects {lh,rh}.aparc.stats Freesurfer derivative file.

    Parameters
    ----------
    session : str
        Must be either "newborn" or "sixmonth".
    hemisphere : str
        Can be 'lh' or 'rh', which gets the file for only the left or right
        hemisphere, respectively. Corresponds to the `--hemi` flag of
        aparcstats_2table. Default is "lh".
    
    Returns
    -------
    exit code : None
        Returns ``None``. If Succesful, a text file will be saved to
        `aparc_{session}_{hemisphere}.csv` in the same directory as this script.
    
    Notes
    -----
    See: https://surfer.nmr.mgh.harvard.edu/fswiki/aparcstats2table
    
    aparcstats2table on Freesurfer 7.1.1 does not work with the {lh, rh}.parc.stats
    files saved by Nibabies 24. This is why we load them manually and build our
    own dataframe.
    """
    ses_dir = "six_month" if session == "sixmonth" else session
    dpath = PROJECT_PATH / f"{ses_dir}/derivatives/Nibabies_auto/sourcedata/freesurfer"

    this_dir = (Path(__file__).parent).resolve()

    fpath_sublist = this_dir / f"dec_{session}.table.dat"
    out_fpath = this_dir / f"aparc_{session}_{hemisphere}.csv"

    # /Volumes/HumphreysLab/Daily_2/BABIES/MRI/newborn/derivatives/Nibabies_auto/sourcedata/freesurfer/sub-1176_ses-newborn/stats/lh.aparc.stats
    stats_paths = list(dpath.rglob(f"sub-*/stats/{hemisphere}.aparc.stats"))
    dfs = []
    for stat_path in stats_paths:
        print(".", end="")
        # find the part of the path that contains sub-{id}_session-{session}
        study_id = [part for part in stat_path.parts if part.startswith("sub-")]
        assert len(study_id) == 1
        # get the str from the list
        study_id = study_id[0]
        # split the sub-{id}_ses-{session} string at the underscore
        study_id = study_id.split("_", maxsplit=1)
        assert study_id
        study_id = study_id[0]
        assert study_id.startswith("sub")
        # read the file into pandas
        df = pd.read_csv(stat_path)
        df["study_id"] = study_id
        dfs.append(df)
    # now create one DataFrame
    df_dataset = pd.concat(dfs, axis=0).set_index("study_id")
    df_dataset.to_csv(out_fpath)
    return

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="get_freesurfer_stats",
        description="Get Freesurfer *.stats files from Nibabies/derivatives/sourcedata/freesurfer/sub-*",
    )
    parser.add_argument(
        "--session",
        dest="session",
        choices=["newborn", "sixmonth"],
        required=True,
    )
    parser.add_argument(
        "--metric",
        dest="metric",
        choices=["aseg", "aparc"],
        default="aseg",
        help="Whether to get volumetric outputs (brainvol.stats. also runs asegstats2tabls) or surface outputs (aparc.stats)"
    )
    parser.add_argument(
        "--hemispheres",
        dest="hemisphere",
        choices=["lh", "rh"],
        default="lh",
        help="If --metric is aparc, this specifies whether to get the lh.aparc.stats file or the rh.aparc.stats file"
    )
    args = parser.parse_args()

    if args.metric == "aseg":
        run_aseg2stats(
            session=args.session,
        )
    elif args.metric == "aparc":
        run_aparcstats2table(
            session=args.session,
            hemisphere=args.hemisphere,
        )