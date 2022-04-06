import sys

sys.path.append("../")
import pandas as pd
from sklearn.neighbors import BallTree
import numpy as np


def distance():
    dfa = pd.read_csv("calls_for_service_3_21_2022_coordinates.csv")

    dfb = pd.read_csv("new_orleans_cameras_3_11_2022.csv")

    bt = BallTree(np.deg2rad(dfa[["latitude", "longitude"]].values), metric="haversine")
    distances, indices = bt.query(np.deg2rad(np.c_[dfb["latitude"], dfb["longitude"]]))

    l = []
    for d in distances:
        miles = d * 3958.8
        yards = miles * 1760
        l.append(yards)
        df = pd.DataFrame(l, columns=["distances"])

    # avg distance: df.distances.sum()/len(df)
    
    # nearest call for service to camera: 16.67260112 is the avg distance in yards for the 432 known NOPD cameras

    # nearest camera to a call for service: 350.3729814 is the avg distance in yards for the 79763 calls for service

    # resource
    # https://towardsdatascience.com/using-scikit-learns-binary-trees-to-efficiently-find-latitude-and-longitude-neighbors-909979bd929b

    return dfa
