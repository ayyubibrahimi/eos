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
    return df