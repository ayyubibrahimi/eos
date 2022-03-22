import sys

sys.path.append("../")
import pandas as pd
from geopy.geocoders import GoogleV3


def convert_coordinates_to_address():
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


def extract_zip(df):
    zips = df.address.str.lower().str.strip().str.extract(r"la (\w{5})\,")

    df.loc[:, "zip"] = zips[0].fillna("")
    return df[~((df.zip == ""))]


def filter_zips_calls_for_service(df):
    df.loc[:, "zip"] = (
        df.zip.str.lower().str.strip().str.replace(r"none", "", regex=True)
    )
    df = df[["zip", "set"]]
    return df


def drop_rows_missing_zip_calls_for_service(df):
    df.loc[:, "zip"] = df.zip.fillna("")
    return df[~((df.zip == ""))].value_counts()


def filter_zips_cameras(df):
    df = df[["zip", "set"]]
    return df.value_counts()


def zipcodes():
    dfa = (
        pd.read_csv("calls_for_service_2022_3_21_2022.csv")
        .pipe(filter_zips_calls_for_service)
        .pipe(drop_rows_missing_zip_calls_for_service)
    )

    dfb = (
        pd.read_csv("camera_zips.csv")
        .rename(columns={"0": "address", "cameras": "coordinates"})
        .pipe(extract_zip)
        .pipe(filter_zips_cameras)
    )

    df = pd.concat([dfa, dfb], axis=0)
    return df
