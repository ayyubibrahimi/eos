import pandas as pd
from geopy.geocoders import GoogleV3
from scipy import spatial
import numpy as np

CAMERA_LOCATIONS_CSV = './data/new_orleans_cameras_3_11_2022.csv'
CALLS_FOR_SERVICE_CSV = './data/calls_for_service_2022_3_21_2022.csv'
CAMERAS_ZIP_CSV = './data/camera_zips.csv'


def convert_coordinates_to_address():
    cameras = pd.read_csv(CAMERA_LOCATIONS_CSV).drop(columns=["set"])
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
        pd.read_csv(CALLS_FOR_SERVICE_CSV)
        .pipe(filter_zips_calls_for_service)
        .pipe(drop_rows_missing_zips)
    )

    dfb = (
        pd.read_csv(CAMERAS_ZIP_CSV)
        .rename(columns={"0": "address", "cameras": "coordinates"})
        .pipe(extract_zips)
        .pipe(filter_zips_cameras)
    )

    df = pd.concat([dfa, dfb], axis=0)
    return df


def extract_coordinates(df):
    points = (
        df.location.str.lower()
        .str.strip()
        .str.replace(r"point ", "", regex=True)
        .str.extract(r"^\((.+) (.+)\)")
    )

    df.loc[:, "latitude"] = points[1].str.replace(r"^0$", "", regex=True)
    df.loc[:, "longitude"] = points[0].str.replace(r"^0$", "", regex=True)

    df = df[["latitude", "longitude"]]
    return df[~((df.latitude == "") & (df.longitude == ""))]


def distance_from_calls_to_camera():
    print("Loading calls for service...")
    calls_for_service_df = pd.read_csv(CALLS_FOR_SERVICE_CSV).pipe(extract_coordinates)

    print("Loading camera locations...")
    camera_locations_df = pd.read_csv(CAMERA_LOCATIONS_CSV)

    print("Pre-processing data...")
    calls_for_service_list = list(zip(calls_for_service_df.latitude, calls_for_service_df.longitude))
    camera_locations_list = list(zip(camera_locations_df.latitude, camera_locations_df.longitude))
    camera_locations_coordinates = np.array(camera_locations_list)

    all_distances = []
    print("Computing distances...")
    for camera_location_coordinates in camera_locations_coordinates[0:5]:
        tree = spatial.KDTree(calls_for_service_list)
        distances = tree.query([camera_location_coordinates])
        print(distances)
        all_distances.append(distances)

    all_distances_df = pd.DataFrame(all_distances, columns=["distance", "index"])
    all_distances_df.loc[:, "distance"] = all_distances_df.distance.astype(str).str.replace(
        r"(\[|\])", "", regex=True
    )
    # avg distance of cameras to a call for service = 0.000146764

    # avg distance of calls for service to a camera = 0.003092017

    return all_distances_df
