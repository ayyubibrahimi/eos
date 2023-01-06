import pandas as pd


def standardize_item_numbers(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    """Cleans and standardizes item number columns

    Args:
        df (pd.DataFrame):
            the frame to process
        cols (list of str):
            item number columns

    Returns:
        the updated frame
    """
    for col in cols:
        df.loc[:, col] = (
            df[col]
            .str.strip()
            .str.lower()
            .str.replace(r"-", "", regex=False)
        )
    return df
    

def standardize_and_drop_rows_w_na_values(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    """Drops rows with na values

    Args:
        df (pd.DataFrame):
            the frame to process
        cols (list of str):
            cols

    Returns:
        the updated frame
    """
    for col in cols:
        df.loc[:, col] = (
            df[col]
            .str.strip()
            .str.lower()
            .fillna("")
        )
        df = df[~((df.loc[:, col]) == "")]
    return df