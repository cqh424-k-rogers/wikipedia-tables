import re
from io import StringIO

import pandas as pd
import requests

URL = "https://en.wikipedia.org/wiki/List_of_countries_by_life_expectancy"



def get_tables(html_file=None):
    if html_file:
        html = open(html_file, encoding="utf-8").read()
    else:
        headers = {"User-Agent": "wiki-table-assignment/1.0 (student project)"}
        html = requests.get(URL, headers=headers, timeout=30).text
    return pd.read_html(StringIO(html))



def remove_footnotes(text):
    text = re.sub(r"\[.*?\]", "", str(text))     
    text = re.sub(r"[†‡*§]", "", text)            
    return text.strip()


def to_number(column):
    column = column.map(remove_footnotes)
    column = column.str.replace("\u2212", "-", regex=False)   
    column = column.str.replace(",", "", regex=False)
    column = column.str.extract(r"(-?\d+\.?\d*)")[0]
    return pd.to_numeric(column, errors="coerce")


def clean_table(df, prefix):
    
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [" ".join(dict.fromkeys(map(str, c))) for c in df.columns]
    df.columns = [re.sub(r"\W+", "_", remove_footnotes(c)).strip("_").lower()
                  for c in df.columns]

    
    text_cols = [c for c in df.columns if not pd.api.types.is_numeric_dtype(df[c])]
    country_col = max(text_cols, key=lambda c: df[c].nunique())
    df = df.rename(columns={country_col: "country"})

    
    df["country"] = df["country"].map(remove_footnotes)
    df["country"] = df["country"].str.replace(r"^[^\w(]+", "", regex=True)
    df = df[~df["country"].str.lower().isin(["world", "total", "country", ""])]

    
    for col in list(df.columns):
        if col == "country":
            continue
        numbers = to_number(df[col])
        if numbers.notna().mean() > 0.6:
            df[col] = numbers
        else:
            df = df.drop(columns=col)

   
    df["key"] = df["country"].str.lower().str.replace(r"\(.*?\)", "", regex=True)
    df["key"] = df["key"].str.normalize("NFKD").str.encode("ascii", "ignore").str.decode("ascii")
    df["key"] = df["key"].str.replace(r"[^a-z0-9 ]", "", regex=True).str.strip()
    df = df.drop_duplicates("key")

    
    df = df.rename(columns={c: f"{prefix}_{c}" for c in df.columns
                            if c not in ("country", "key")})
    return df


tables = get_tables()                 
big_tables = [t for t in tables if len(t) >= 50]
print(f"Found {len(tables)} tables, {len(big_tables)} with 50+ rows")

table_a = clean_table(big_tables[0], "a")
table_b = clean_table(big_tables[1], "b")

merged = table_a.merge(table_b, on="key", how="outer", indicator=True)
merged["country"] = merged["country_x"].fillna(merged["country_y"])
merged["in_both_tables"] = merged["_merge"] == "both"
merged = merged.drop(columns=["country_x", "country_y", "key", "_merge"])
merged = merged.sort_values("country")

merged.to_csv("clean.csv", index=False)
print(f"Saved clean.csv with {len(merged)} rows")
print(merged.head())
merged = merged.sort_values("country")

