# corporate_kinship

Extraction code for the HTRC Data Capsule `sp_register_extraction`. Turns OCR page
text from the S&P / Poor's Register of Corporations, Directors and Executives into
structured tabular records.

## parse_register.py

Reads the per-page OCR `.txt` files of a downloaded HathiTrust volume, segments the
Directors & Executives section into individual person records, and extracts fields.

Run inside the capsule (secure mode) over a volume fetched with `htrc download`:

```
python3 parse_register.py /media/secure_volume/vols --htid uc1.c2583485 --year 1912 --out persons.csv
```

### Output schema (persons CSV, one row per person)

| column | meaning |
|--------|---------|
| ht_volume_id | HathiTrust volume id the entry came from |
| source_volume_year | year of the register volume |
| surname | surname (as printed) |
| given_name | first given name |
| middle_name | remaining given names / initials |
| suffix | Jr / Sr / II / III / IV if present |
| birth_year | year from a `(b. YYYY ...)` clause |
| birth_place | place from a `(b. YYYY PLACE ...)` clause |
| raw_entry | full reconstructed entry text (for downstream affiliation parsing) |

Record boundaries are detected by all-caps `SURNAME,` headers; line-wrap hyphenation
is rejoined. The person-firm-year panel (exploding `raw_entry` into firm + title rows)
is the next stage.
