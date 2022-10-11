import pandas as pd
from sklearn.neighbors import BallTree
import numpy as np


CAMERA_LOCATIONS_CSV = './data/new_orleans_cameras_3_11_2022.csv'
CALLS_FOR_SERVICE_CSV = './data/calls_for_service_2022_9_14_2022.csv'

def distance_from_calls_to_camera():
    print("Loading calls for service...")
    dfa = pd.read_csv(CALLS_FOR_SERVICE_CSV)
    # filter for violent crimes (list of all crimes below)
    print("Pre-processing data...")
    dfa = dfa[
        (
            dfa.TypeText.isin(
                [
                    "AGGRAVATED ASSAULT",
                    "CARJACKING",
                    "AGGRAVATED ASSAULT DOMESTIC",
                    "ARMED ROBBERY WITH GUN",
                    "AGGRAVATED BATTERY BY SHOOTING",
                    "AGGRAVATED BATTERY DOMESTIC",
                    "AGGRAVATED BURGLARY",
                    "AGGRAVATED BATTERY BY CUTTING",
                    "AGGRAVATED RAPE",
                    "ARMED ROBBERY",
                    "SIMPLE RAPE",
                    "HOMICIDE BY SHOOTING",
                    "ARMED ROBBERY WITH KNIFE",
                    "AGGRAVATED KIDNAPPING",
                    "SIMPLE ASSAULT DOMESTIC",
                    "AGGRAVATED RAPE UNFOUNDED BY SPECIAL VICTIMS OR CHILD ABUSE",
                    "AGGRAVATED BURGLARY DOMESTIC",
                    "AGGRAVATED RAPE MALE VICTIM",
                    "HOMICIDE",
                    "HOMICIDE BY CUTTING",
                    "ILLEGAL CARRYING OF WEAPON- KNIFE",
                    "SIMPLE RAPE MALE VICTIM",
                    "AGGRAVATED ARSON",
                    "SIMPLE RAPE UNFOUNDED BY SPECIAL VICTIMS OR CHILD ABUSE",
                ]
            )
        )
    ]

    dfa.loc[:, "TypeText"] = dfa.TypeText.fillna("")
    dfa = dfa[~(dfa.TypeText == "")]

    locations = (
        dfa.Location.str.lower()
        .str.strip()
        .str.extract(r"point \((-.+\..+) (.+\..+)\)")
    )

    dfa.loc[:, "latitude"] = locations[1].fillna("")
    dfa = dfa[~((dfa.latitude == ""))]
    dfa.loc[:, "latitude"] = dfa.latitude.astype(float)
    dfa.loc[:, "longitude"] = locations[0].fillna("")
    dfa = dfa[~((dfa.longitude == ""))]
    dfa.loc[:, "longitude"] = dfa.longitude.astype(float)

    dfb = pd.read_csv(CAMERA_LOCATIONS_CSV)
    print("Loading camera locations...")

    bt = BallTree(np.deg2rad(dfa[["latitude", "longitude"]].values), metric="haversine")
    distances, indices = bt.query(np.deg2rad(np.c_[dfb["latitude"], dfb["longitude"]]))

    l = []
    print("Computing distances...")
    for d in distances:
        miles = d * 3958.8
        yards = miles * 1760
        l.append(yards)
        distance_df = pd.DataFrame(l, columns=["distances"])
    avg = distance_df.distances.sum()/len(distance_df)

    num_cameras = 432
    calc = f"Average distance from a camera ({num_cameras} cameras) to a call for service is {avg} yards "
    return calc

