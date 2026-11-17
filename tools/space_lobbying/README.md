Builds `data/space_lobbying.json`: lobbying filed by or for the atlas's own spaces.

Run from a scratch folder (the scripts write their caches beside where they run):

1. `sweep.py museum gallery "art museum" ...` collects LDA client records by keyword.
2. `pername.py` looks up every US space by its own name.
3. `filings.py` pulls every filing for the matched clients; `agg.py` dedupes amendments and totals each year.
4. `match_eu.py` matches the EU Transparency Register XML export (transparency-register.europa.eu/odplastorganisationxml_en; strip XML 1.1 control-character references first) by website and name.

Every match was checked by hand afterwards; namesakes were dropped in `agg.py` and the EU entries were written from the register records.
