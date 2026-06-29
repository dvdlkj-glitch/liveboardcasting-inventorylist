# Ulive Smart Fulfillment — Streamlit App

Animated intro tour, then a **real upload-and-match demo** driven by your own data.

## How it works

1. **Intro tour** plays at the top (Skip / Enter the Demo buttons scroll you down).
2. **Live Demo** — upload two Excel import files, or tick *Use included sample*, then **Run AI Matching**:
   - **Customer Orders** (`orders_import.xlsx`) — built from the slist 1–3 invoice PDFs.
   - **Stock Received** (`stock_import.xlsx`) — built from `China Stock Listing.xlsx` (4 supplier sheets).
3. The engine matches every ordered line to received stock — **by item code first, then fuzzy product name** — and shows confirmed / partial / not-received counts, fill rate, per-supplier receiving, a filterable line table, and a Fulfill / Hold recommendation.

## Files to deploy (keep together)

```
streamlit_app.py      # the app
requirements.txt
tour_hero.html        # intro tour (asset)
theme_style.html      # shared dark theme (asset)
orders_import.xlsx    # sample orders (real, parsed from the PDFs)
stock_import.xlsx     # sample stock (real, parsed from the Excel)
```

## Import file formats

**Orders** — columns: `invoice, customer, item_code, description, qty_ordered, unit_price, line_total`
**Stock**  — columns: `supplier, item_code, description, qty_received, barcode`

Column detection is flexible (it looks for code / description / quantity headers, English or Chinese), so lightly-different headers still work.

## Regenerating the import files from new raw data

`parse_data.py` rebuilds the two import files from the raw PDFs + Excel:

```bash
pip install pdfplumber openpyxl
python parse_data.py
```

## Run locally

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## Deploy on Streamlit Community Cloud

Push the folder above to a GitHub repo, then create a new app pointing at `streamlit_app.py`.
