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