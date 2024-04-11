import json
import os
from datetime import datetime
from typing import Union
from zoneinfo import ZoneInfo

import pandas as pd


def create_file(base_path: str, filename: str):

    file_path: str = os.path.join(base_path, filename)
    if os.path.isfile(file_path):
        os.remove(file_path)
    return file_path


def flatten_dict(d: dict, parent_key: str = '', sep: str = '_'):

    items: list = []
    for k, v in d.items():
        new_key: str = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def convert_to_dataframe(data):

    data_new_keys = [flatten_dict(d) for d in data]
    df: pd.DataFrame = pd.DataFrame(data_new_keys)
    return df


def save_json_file(base_path, filename: str, data: list) -> None:

    file_path: str = create_file(base_path, filename)
    with open(file_path, "w") as open_file:
        json.dump(data, open_file, sort_keys=True, indent=4, ensure_ascii=False)


def save_csv_file(base_path: str, filename: str, data: Union[list, pd.DataFrame]) -> None:

    file_path: str = create_file(base_path, filename)
    if isinstance(data, list):
        df: pd.DataFrame = convert_to_dataframe(data)
        df.to_csv(f'{file_path}', index=False)
    else:
        data.to_csv(f'{file_path}', index=False)


def save_excel_file(base_path: str, filename: str, data: Union[list, pd.DataFrame]) -> None:

    file_path: str = create_file(base_path, filename)
    if isinstance(data, list):
        df: pd.DataFrame = convert_to_dataframe(data)
        df.to_excel(f'{file_path}', index=False)
    else:
        data.to_excel(f'{file_path}', index=False)


def save_binary_file(base_path: str, filename: str, data: Union[list, pd.DataFrame]) -> None:

    file_path: str = create_file(base_path, filename)
    if isinstance(data, list):
        df: pd.DataFrame = convert_to_dataframe(data)
        df.to_feather(f'{file_path}')
    else:
        data.to_feather(f'{file_path}')


def save_pickle_file(base_path: str, filename: str, data: Union[list, pd.DataFrame]) -> None:

    file_path: str = create_file(base_path, filename)
    if isinstance(data, list):
        df: pd.DataFrame = convert_to_dataframe(data)
        df.to_pickle(f'{file_path}')
    else:
        data.to_pickle(f'{file_path}')


def convert_date(date_str: str, date_format: str) -> str:

    date: datetime = datetime.strptime(date_str, date_format)
    brasilia_datetime: datetime = date.replace(tzinfo=ZoneInfo('America/Sao_Paulo'))
    # return brasilia_datetime.strftime("%Y-%m-%d %H:%M:%S %Z%z")
    return brasilia_datetime.strftime("%Y-%m-%d %H:%M:%S")
