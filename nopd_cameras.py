import sys

sys.path.append("../")
import pandas as pd
from geopy.geocoders import GoogleV3
from scipy import spatial
import numpy as np


## code below joins the camera and calls for service dataframes on coordinates


def extract_coordinates_from_calls_for_service(df):
    points = (
        df.location.str.lower()
        .str.strip()
        .str.replace(r"point ", "", regex=True)
        .str.extract(r"^\((.+) (.+)\)")
    )

    df.loc[:, "latitude"] = points[1].str.replace(r"^0$", "", regex=True)
    df.loc[:, "longitude"] = points[0].str.replace(r"^0$", "", regex=True)

    df = df[["latitude", "longitude", "set"]]
    return df[~((df.latitude == "") & (df.longitude == ""))]


def join_coordinates():
    dfa = pd.read_csv("calls_for_service_3_21_2022.csv").pipe(
        extract_coordinates_from_calls_for_service
    )

    dfb = pd.read_csv("new_orleans_cameras_3_11_2022.csv")

    df = pd.concat([dfa, dfb], axis=0)
    return df


### code below creates joins cameras and calls_for_services on zip codes


def convert_camera_coordinates_to_address():
    cameras = pd.read_csv("new_orleans_cameras_3_11_2022.csv").drop(columns=["set"])
    df = pd.DataFrame(cameras, columns=["latitude", "longitude"])
    gkey = ""
    geolocator = GoogleV3(api_key=gkey)

    df["point"] = list(zip(df["latitude"], df["longitude"]))

    locations = []
    for row in df["point"]:
        address = geolocator.reverse(row)
        locations.append(address)
        df = pd.DataFrame(locations)
    return df


def extract_zips(df):
    zips = df.address.str.lower().str.strip().str.extract(r"la (\w{5})\,")

    df.loc[:, "zip"] = zips[0].fillna("")
    return df[~((df.zip == ""))]


def filter_zips_calls_for_service(df):
    df.loc[:, "zip"] = (
        df.zip.str.lower().str.strip().str.replace(r"none", "", regex=True)
    )
    df = df[["zip", "set"]]
    return df


def drop_rows_missing_zips(df):
    df.loc[:, "zip"] = df.zip.fillna("")
    return df[~((df.zip == ""))].value_counts()


def filter_zips_cameras(df):
    df = df[["zip", "set"]]
    return df.value_counts()


def concat_zips():
    dfa = (
        pd.read_csv("calls_for_service_2022_3_21_2022.csv")
        .pipe(filter_zips_calls_for_service)
        .pipe(drop_rows_missing_zips)
    )

    dfb = (
        pd.read_csv("camera_zips.csv")
        .rename(columns={"0": "address", "cameras": "coordinates"})
        .pipe(extract_zips)
        .pipe(filter_zips_cameras)
    )

    df = pd.concat([dfa, dfb], axis=0)
    return df
