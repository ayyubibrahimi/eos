import sys

sys.path.append("../")
import pandas as pd
from sklearn.neighbors import BallTree
import numpy as np


def distance():
    dfa = pd.read_csv("calls_for_service_2022_9_14_2022.csv")

    # filter for violent crimes (list of all crimes below)
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

    dfb = pd.read_csv("new_orleans_cameras_3_11_2022_french_quarter_filtered.csv")

    bt = BallTree(np.deg2rad(dfa[["latitude", "longitude"]].values), metric="haversine")
    distances, indices = bt.query(np.deg2rad(np.c_[dfb["latitude"], dfb["longitude"]]))

    l = []
    for d in distances:
        miles = d * 3958.8
        yards = miles * 1760
        l.append(yards)
        df = pd.DataFrame(l, columns=["distances"])

    # Nearest camera to a violent crime: 148 is the avg distance in yards from a camera (432) to a violent crime
    # Nearest call for service to a camera: 316 the avg distance in yards from a violent crime (2250) to a camera
    # Note: as of 6-7, there were 2250 calls for service for violent crimes, as defined above
    # using the 6-7 data, I did an calculated avg distances in yards with an alternative filtering of crimes

    # add identifer for camera

    # filter 2: 35, and 372 are the avg distances in yards
    """
      "BUSINESS BURGLARY",
                    "CARJACKING",
                    "AGGRAVATED ASSAULT",
                    "SIMPLE BURGLARY VEHICLE",
                    "DOMESTIC DISTURBANCE",
                    "HIT & RUN",
                    "SIMPLE BURGLARY",
                    "AGGRAVATED ASSAULT DOMESTIC",
                    "RECKLESS DRIVING",
                    "DISCHARGING FIREARM",
                    "SIMPLE BATTERY",
                    "HIT & RUN WITH INJURIES",
                    "SIMPLE BATTERY DOMESTIC",
                    "RESIDENCE BURGLARY",
                    "AGGRAVATED BATTERY BY SHOOTING",
                    "SIMPLE ROBBERY",
                    "AGGRAVATED BATTERY DOMESTIC",
                    "FIGHT",
                    "AGGRAVATED BURGLARY",
                    "AGGRAVATED BATTERY BY CUTTING",
                    "AGGRAVATED RAPE",
                    "SIMPLE BURGLARY DOMESTIC",
                    "ARMED ROBBERY",
                    "SIMPLE RAPE",
                    "SIMPLE ROBBERY",
                    "AGGRAVATED BATTERY",
                    "HOMICIDE BY SHOOTING",
                    "ARMED ROBBERY WITH KNIFE",
                    "AGGRAVATED KIDNAPPING",
                    "SEXUAL BATTERY",
                    "SIMPLE KIDNAPPING",
                    "MISDEMEANOR SEXUAL BATTERY",
                    "SIMPLE ASSAULT DOMESTIC",
                    "HIT & RUN POLICE VEHICLE",
                    "SIMPLE ASSAULT",
                    "AGGRAVATED RAPE UNFOUNDED BY SPECIAL VICTIMS OR CHILD ABUSE",
                    "AGGRAVATED BURGLARY DOMESTIC",
                    "AGGRAVATED RAPE MALE VICTIM",
                    "OFFICER NEEDS ASSISTANCE, LIFE IN DANGER",
                    "SIMPLE ARSON",
                    "HOMICIDE",
                    "HIT & RUN CITY VEHICLE",
                    "HOMICIDE BY CUTTING",
                    "EXPLOSION",
                    "SIMPLE RAPE MALE VICTIM",
                    "FIREBOMB",
                    "AGGRAVATED ARSON",
                    "SIMPLE RAPE UNFOUNDED BY SPECIAL VICTIMS OR CHILD ABUSE",
                    "HOSTAGE SITUATION",
                    "HIT & RUN FATALITY",
    """

    # all crimes
    """ 'BUSINESS BURGLARY', 'RECOVERY OF REPORTED STOLEN VEHICLE',
       'COMPLAINT OTHER', 'MEDICAL',xc 'CARJACKING', 'AGGRAVATED ASSAULT',
       'SIMPLE BURGLARY VEHICLE', 'UNAUTHORIZED USE OF VEHICLE',
       'SIMPLE CRIMINAL DAMAGE', 'DOMESTIC DISTURBANCE', 'AUTO ACCIDENT',
       'HIT & RUN', 'THEFT', 'AUTO THEFT', 'PICKPOCKET',
       'DISTURBANCE (OTHER)', 'SUSPICIOUS PERSON', 'ABANDONED VEHICLE',
       'RETURN FOR ADDITIONAL INFO', 'MENTAL PATIENT', 'SIMPLE BURGLARY',
       'EXTORTION (THREATS)', 'BURGLAR ALARM, SILENT',
       'AGGRAVATED ASSAULT DOMESTIC', 'RECKLESS DRIVING',
       'CRIMINAL DAMAGE DOMESTIC', 'LOST PROPERTY', 'TRAFFIC INCIDENT',
       'DISCHARGING FIREARM', 'MISSING JUVENILE', 'SIMPLE BATTERY',
       'SILENT 911 CALL', 'RECOVERY OF VEHICLE',
       'HIT & RUN WITH INJURIES', 'THEFT BY FRAUD',
       'ARMED ROBBERY WITH GUN', 'SIMPLE BATTERY DOMESTIC', 'DEATH',
       'AUTO ACCIDENT WITH INJURY', 'AREA CHECK', 'BURGLAR ALARM, LOCAL',
       'NOISE COMPLAINT', 'VEHICLE NO-PURSUIT', 'BUSINESS CHECK',
       'TRAFFIC STOP', 'TOW IMPOUNDED VEHICLE (PRIVATE)',
       'RESIDENCE BURGLARY', 'AGGRAVATED BATTERY BY SHOOTING',
       'DRIVING WHILE UNDER INFLUENCE', 'PROWLER', 'SIMPLE ROBBERY',
       'BURGLAR ALARM, SILENT, FAR NO RESPONSE', 'INDECENT BEHAVIOR',
       'SHOPLIFTING', 'SIMULTANEOS STOLEN/RECOVERY VEHICLE',
       'INCIDENT REQUESTED BY ANOTHER AGENCY', 'CRUELTY TO ANIMALS',
       'MISSING ADULT', 'AGGRAVATED CRIMINAL DAMAGE',
       'AGGRAVATED BATTERY DOMESTIC', 'FIGHT', 'OBSCENITY, EXPOSING',
       'HOLD UP ALARM', 'THEFT FROM EXTERIOR OF VEHICLE',
       'DIRECTED PATROL', 'DRUG VIOLATIONS', 'FIRE', 'FIREWORKS',
       'SUICIDE THREAT', 'ILLEGAL CARRYING OF WEAPON- GUN',
       'AGGRAVATED BURGLARY', 'AGGRAVATED BATTERY BY CUTTING',
       'AGGRAVATED RAPE', 'SIMPLE BURGLARY DOMESTIC',
       'FUGITIVE ATTACHMENT', 'ARMED ROBBERY', 'SIMPLE RAPE',
       'AUTO ACCIDENT CITY VEHICLE', 'RESIDENCE CHECK',
       'EXTORTION (THREATS) DOMESTIC', 'AGGRAVATED BATTERY',
       'UNCLASSIFIED DEATH', 'SIMPLE ROBBERY, PROPERTY SNATCHING',
       'VIOLATION OF PROTECTION ORDER', 'HOMICIDE BY SHOOTING',
       'ARMED ROBBERY WITH KNIFE', 'WALKING BEAT', 'SUICIDE ATTEMPT',
       'AUTO ACCIDENT POLICE VEHICLE', 'AGGRAVATED KIDNAPPING',
       'MUNICIPAL ATTACHMENT', 'SEXUAL BATTERY', 'WARR STOP WITH RELEASE',
       'SIMPLE KIDNAPPING', 'HOMELESS', 'VEHICLE PURSUIT',
       'CRIMINAL MISCHIEF', 'SUICIDE', 'MISDEMEANOR SEXUAL BATTERY',
       'BICYCLE THEFT', 'DIRECTED TRAFFIC ENFORCEMENT', 'PROSTITUTION',
       'BOMB SCARE', 'SIMPLE ASSAULT DOMESTIC', 'AUTO ACCIDENT FATALITY',
       'MEDICAL SEXUAL ASSAULT KIT PROCESSING', 'QUALITY OF LIFE ISSUE',
       'HIT & RUN POLICE VEHICLE', 'SEXTING',
       'CONTRIBUTING TO DELINQUENCY', 'SIMPLE ESCAPE',
       'CARJACKING- NO WEAPON', 'CURFEW VIOLATION', 'SIMPLE ASSAULT',
       'REFERRAL TO MHSD', 'MEDICAL - NALOXONE',
       'AGGRAVATED RAPE UNFOUNDED BY SPECIAL VICTIMS OR CHILD ABUSE',
       'AGGRAVATED BURGLARY DOMESTIC', 'AGGRAVATED RAPE MALE VICTIM',
       'NEGLIENT INJURY', 'OFFICER NEEDS ASSISTANCE, LIFE IN DANGER',
       'ILLEGAL CARRYING OF WEAPON', 'TRUANT VIOLATION',
       'THEFT BY EMBEZZLEMENT', 'TRAFFIC CONGESTION',
       'TRAFFIC ATTACHMENT', 'SIMPLE ARSON', 'CRIMINAL MISCHIEF DOMESTIC',
       'HOMICIDE', 'HIT & RUN CITY VEHICLE', 'HOMICIDE BY CUTTING',
       'POSSESSION OF STOLEN PROPERTY', 'PUBLIC GATHERING',
       'ASSET SEIZURE', 'SUSPICIOUS PACKAGE',
       'SEX OFFENDER REGISTRATION CHECK', 'DISPERSE SUBJECTS',
       'VIDEO VOYEURISM', 'JUVENILE ATTACHMENT',
       'ILLEGAL CARRYING OF WEAPON- KNIFE', 'BLIGHTED PROPERTY',
       'EXPLOSION', 'EMS UNIT NEEDS ASSISTANCE', 'PARADE ITEM NUMBER',
       'ABANDONED BOAT', 'SIMPLE RAPE MALE VICTIM', 'FLOOD EVENT',
       'ICING ON ROADS', 'FORGERY', 'DRUNK', 'PROTEST', 'FIREBOMB',
       'AGGRAVATED ARSON', 'BARRICADE ERECTED',
       'SOLICITING FOR PROSTITUTION', 'ISSUING WORTHLESS CHECKS',
       'ATTACHMENT',
       'SIMPLE RAPE UNFOUNDED BY SPECIAL VICTIMS OR CHILD ABUSE',
       'HOSTAGE SITUATION', 'OFFICER NEEDS ASSISTANCE',
       'HIT & RUN FATALITY'"""

    return df
