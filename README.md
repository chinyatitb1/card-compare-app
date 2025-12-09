# Smartcard Comparison Tool

A simple web app to compare **distinct smartcard numbers** between two datasets.

Built with [Streamlit](https://streamlit.io/) and developed by **Tinashe Chinyati**.

---

## Features

- Upload **two files** (CSV or Excel, non-password-protected)
- Select which column represents the **smartcard number** in each file
- Automatically:
  - Normalises smartcard numbers to **strings** (no `.0` issues)
  - Computes distinct smartcards in each file
- View:
  - Smartcards present **in both files**
  - Smartcards **only in File A**
  - Smartcards **only in File B**
- Download each result set as **CSV**
- Clean, modern UI with summary metrics and file structure overview

---

## Tech Stack

- Python
- Streamlit
- pandas
- numpy
- openpyxl (for Excel support)

---

## Running Locally

1. Clone the repo:

   ```bash
   git clone https://github.com/chinyatitb1/card-compare-app.git
   cd smartcard-compare-app


