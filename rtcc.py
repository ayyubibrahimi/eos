import sys
sys.path.append("../")
import pandas as pd



def clean():

    df1 = pd.read_csv("electronic_police_report_2018.csv")
    df2 = pd.read_csv("electronic_police_report_2019.csv")
    df3 = pd.read_csv("electronic_police_report_2020.csv")
    df4 = pd.read_csv("electronic_police_report_2021.csv")
    df5 = pd.read_csv("electronic_police_report_2022.csv")
    
    dfs = [df1, df2, df3, df4, df5]

    dfa = pd.concat(dfs, join="outer")
    
    dfb = pd.read_csv("rtcc.csv", encoding="cp1252").rename(columns={"Item_number": "item_number"})
    
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
    df.loc[:, "offender_gender"] = df.offender_gender.str.lower().str.strip().fillna("")\
        .str.replace("unknown", "", regex=False)
    df = df[~((df.offender_gender ==  ""))]

    df = df[(df.offender_gender.isin(["female"]))]
    ### male 
    """
    2018  black        0.859627
          non-black    0.140373
    2019  black        0.882860
          non-black    0.117140
    2020  black        0.930614
          non-black    0.069386
    2021  black        0.880707
          non-black    0.119293
    2022  black        0.875145
          non-black    0.124855 """

    ### female
    """
    2018  black        0.718876
          non-black    0.281124
    2019  black        0.883077
          non-black    0.116923
    2020  black        0.875000
          non-black    0.125000
    2021  black        0.848259
          non-black    0.151741
    2022  black        0.934783
          non-black    0.065217 
    """
    return df


def filter_year(df):
    df = df[(df.year.astype(str).isin(["2021"]))]

    ### 2021
    """
    1         black            0.917073
              white            0.060976
              unknown          0.021951
    2         black            0.870833
              white            0.129167
    3         black            0.928000
              unknown          0.056000
              white            0.016000
    4         black            0.809917
              unknown          0.157025
              white            0.033058
    5         black            0.953704
              white            0.024691
              unknown          0.021605
    6         black            0.952239
              unknown          0.023881
              white            0.023881
    7         black            0.903553
              unknown          0.060914
              white            0.032149
              asian            0.001692
              hispanic         0.001692
    8         black            0.792965
              white            0.152764
              unknown          0.048241
              asian            0.004020
              hispanic         0.002010
    """
    return df 

def merged():
    df = pd.read_csv("rtcc_merged.csv")\
        .pipe(filter_race)\
        .pipe(filter_gender)\
        .pipe(filter_year)
    return df 