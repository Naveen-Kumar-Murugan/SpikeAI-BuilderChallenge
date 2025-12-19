import pandas as pd
import os
import gspread
from google.oauth2.service_account import Credentials
from app.logger import get_logger

SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]

def get_gspread_client(credentials_path: str = "credentials.json"):
    creds = Credentials.from_service_account_file(credentials_path, scopes=SCOPES)
    client = gspread.authorize(creds)
    return client

def list_sheet_names(spreadsheet_url: str):
    client = get_gspread_client()
    spreadsheet = client.open_by_url(spreadsheet_url)
    return [ws.title for ws in spreadsheet.worksheets()]

def load_screaming_frog_sheet(spreadsheet_url: str, sheet_name: str) -> pd.DataFrame:
    """
    Load a single sheet and return as DataFrame.
    """
    client = get_gspread_client()
    spreadsheet = client.open_by_url(spreadsheet_url)
    worksheet = spreadsheet.worksheet(sheet_name)
    data = worksheet.get_all_records()
    df = pd.DataFrame(data)
    df.columns = [str(c).strip() for c in df.columns]
    return df

def build_union_table(spreadsheet_url: str) -> pd.DataFrame:
    logger = get_logger(__name__)

    logger.info("Building union table from spreadsheet...")
    client = get_gspread_client()
    spreadsheet = client.open_by_url(spreadsheet_url)

    all_dfs = []

    for ws in spreadsheet.worksheets():
        df = pd.DataFrame(ws.get_all_records())
        if df.empty:
            continue

        df.columns = [str(c).strip() for c in df.columns]

        if "Address" not in df.columns:
            continue

        df["Address"] = (
            df["Address"]
            .astype(str)
            .str.strip()
        )

        all_dfs.append(df)

    if not all_dfs:
        logger.info("No data found in spreadsheet worksheets; returning empty DataFrame")
        return pd.DataFrame()

    union_df = pd.concat(all_dfs, ignore_index=True, sort=False)

    union_df = (
        union_df
        .groupby("Address", as_index=False)
        .first()
    )
    logger.info("Union table built with %d unique addresses.", len(union_df))
    return union_df

