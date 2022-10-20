import sys

sys.path.append("../")
import pandas as pd

"""
rtcc.csv includes all the item numbers for which NOPD has requested RTCC footage.
rtcc item numbers can be merged on item numbers from NOPD's electronic police reports 
"""

def clean():
    df1 = pd.read_csv("electronic_police_report_2018.csv")
    df2 = pd.read_csv("electronic_police_report_2019.csv")
    df3 = pd.read_csv("electronic_police_report_2020.csv")
    df4 = pd.read_csv("electronic_police_report_2021.csv")
    df5 = pd.read_csv("electronic_police_report_2022.csv")

    dfs = [df1, df2, df3, df4, df5]

    dfa = pd.concat(dfs, join="outer")

    dfb = pd.read_csv("rtcc.csv", encoding="cp1252").rename(
        columns={"Item_number": "item_number"}
    )

    df = pd.merge(dfa, dfb, on="item_number")

    # review district
    # review signal description
    # review charge description
    # offender demographics
    return df.to_csv("rtcc_merged.csv", index=False)


def filter_race(df):
    df.loc[:, "offender_race"] = df.offender_race.fillna("").str.lower().str.strip()
    # .str.replace("unknown", "non-black", regex=False)\
    # .str.replace("hispanic", "non-black", regex=False)\
    # .str.replace("asian", "non-black", regex=False)\
    # .str.replace("white", "non-black", regex=False)\
    # .str.replace(r"amer\. ind\.", "non-black", regex=True)
    return df[~((df.offender_race == ""))]


def filter_gender(df):
    df.loc[:, "offender_gender"] = (
        df.offender_gender.str.lower()
        .str.strip()
        .fillna("")
        .str.replace("unknown", "", regex=False)
    )
      # df = df[~((df.offender_gender == ""))]
      # df = df[(df.offender_gender.isin(["female"]))]
      # df.loc[:, "offenderstatus"] = df.offenderstatus.str.lower().str.strip().fillna("")
      # df = df[(df.offenderstatus.isin(["arrested"]))]
    
    return df


def filter_year(df):
    df = df[(df.year.astype(str).isin(["2018", "2019", "2020", "2021", "2022"]))]
    # the following figures are percentages of the "offender_race" value
    ### 2018 - 2022
    """
      black         0.768292
      unknown       0.152651
      white         0.068554
      hispanic      0.009226
      asian         0.001065
      -amer. ind.    0.000213
    """
    ### 2022
    """
      black      0.660252
      unknown    0.297557
      white      0.039230
      asian      0.002961
    """
    ### 2021
    """
      black       0.663802
      unknown     0.279270
      white       0.055209
      asian       0.001074
      hispanic    0.000644
    """
    ### 2020
    """
      black         0.867308
      unknown       0.069408
      white         0.046369
      hispanic      0.016040
      amer. ind.    0.000875
    """
    ### 2019
    """
      black       0.849009
      white       0.091532
      unknown     0.044685
      hispanic    0.013694
      asian       0.001081
    """
    ### 2018
    """
      black       0.804891
      white       0.129187
      unknown     0.046252
      hispanic    0.018075
      asian       0.001595
    """
    return df


def extract_years(df):
    years = df.occurred_date_time.astype(str).str.extract(r"(\w{4})")

    df.loc[:, "year"] = years[0]
    """
      2021    5600
      2020    5370
      2019    4102
      2018    2559
      2022    1492
      """
    return df


def merged():
    df = pd.read_csv("rtcc_merged.csv").pipe(filter_year).pipe(filter_race)
    return df
