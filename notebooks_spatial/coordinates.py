import sys

sys.path.append("../")
import pandas as pd
from geopy.geocoders import GoogleV3


def convert_address_to_coordinates():
    locations = pd.read_csv("data/rtcc_locations_4.csv")
    gkey = ""
    geolocator = GoogleV3(api_key=gkey)

    latitude = []
    longitude = []
    for row in locations["location"]:
        address = geolocator.geocode(row)
        lat, lon = address.latitude, address.longitude
        latitude.append(lat)
        longitude.append(lon)
        coordinates = list(zip(latitude, longitude))
        df = pd.DataFrame(coordinates)
    return df


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


def join_call_for_serice_and_rtcc_coordinates():
    dfa = pd.read_csv("calls_for_service_3_21_2022.csv").pipe(
        extract_coordinates_from_calls_for_service
    )

    dfb = pd.read_csv("new_orleans_cameras_3_11_2022.csv")

    df = pd.concat([dfa, dfb], axis=0)
    return df


def read_safecam_coordinates():
    df = pd.read_csv("safecam_coordinates.csv").rename(
        columns={"0": "latitude", "1": "longitude"}
    )
    return df


def append_safecam_and_rtcc_cameras():
    rtcc = pd.read_csv("new_orleans_cameras_3_11_2022.csv")
    rtcc = pd.DataFrame(rtcc, columns=["latitude", "longitude"])

    rtcc["set"] = "rtcc"

    safecam = pd.read_csv("safecam_coordinates.csv").rename(
        columns={"0": "latitude", "1": "longitude"}
    )

    safecam["set"] = "safecam"

    safecam.to_csv("safecam.csv", index=False)

    rtcc.to_csv("nopd.csv", index=False)
    return safecam


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
