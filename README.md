# wikipedia-tables
Assignment 5
# Wikipedia Table Extraction

## Source
**Page:** https://en.wikipedia.org/wiki/List_of_countries_by_life_expectancy

**Tables used:** two country-level `wikitable`s from this page:
- **Table A** – life expectancy by country (overall / male / female).
- **Table B** – a second country-level life-expectancy measure on the page (e.g. healthy life expectancy).

The script prints which tables it picked. `python wiki_tables.py --list` shows every table with its index and columns.

## How to run
- **On GitHub:** Actions tab → "Build clean.csv" → Run workflow. It commits `clean.csv` to the repo.
- **Locally:** `pip install -r requirements.txt && python wiki_tables.py`

## Cleaning steps
1. **Extract** with `requests` + `pandas.read_html`, keeping only `class="wikitable"` tables.
2. **Column names:** flattened multi-row headers, converted to `snake_case`, made duplicates unique, prefixed `a_` / `b_`.
3. **Text cleanup:** removed footnote markers (`[1]`), symbols (`†`, `*`), extra whitespace, and leading flag/bullet characters from country names.
4. **Types:** converted numeric columns by extracting the first number in each cell (handles commas, unicode minus, units). Placeholders like `—` become `NaN`.
5. **Rows:** removed repeated header rows, aggregate rows (`World`, `Total`), empty rows, and duplicate countries.
6. **Merge:** outer join on a normalized country name (lowercase, accents/punctuation removed, parentheticals dropped). `in_both_tables` marks matched rows.

## Challenges and limitations
- Country names differ across tables (e.g. "Czechia" vs "Czech Republic"); normalization catches most but not all. Check rows where `in_both_tables` is `False`.
- The tables may come from different sources or years, so values aren't strictly comparable.
- Wikipedia is edited often; auto-selection of tables may need adjusting via `TABLE_A` / `TABLE_B`.
