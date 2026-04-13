# Blood Bank Synthetic Data Generator

A realistic synthetic data generator for a national blood bank system.  
Perfect for data analysis, visualization, BI dashboards, quality control, and machine learning experiments in healthcare.

**All data is completely fictional** — no real donors or personal information.

## Features

- Generates 3,000 donors and 10,000 donations with realistic distributions
- Includes seasonality, day-of-week patterns, and ethnic blood group bias
- Simulates collection specialists with different error rates
- Creates sample quality issues, lab TAT, infection screening, antigen typing, and donor questionnaires
- Outputs both Excel (multi-sheet) and individual CSV files

## How to Use

You can run the generator in **two formats** — choose whichever is more convenient for you:

- **`blood_bank_data_generator.py`** — classic Python script (recommended for most users)
- **`blood_bank_data_generator.ipynb`** — Jupyter Notebook (great if you want to explore and modify the code interactively)

### Option 1: Using the Python script (.py)

```bash
# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/blood-bank-data-generator.git
cd blood-bank-data-generator

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the generator
python blood_bank_data_generator.py

### Option 2: Using the Jupyter Notebook (.ipynb)
Simply open blood_bank_data_generator.ipynb in Jupyter Notebook, JupyterLab, VS Code, or Google Colab and run the cells.
Data will be generated in the blood_bank_data/ folder.
Configuration
All main parameters (number of donors, donations, date range, region weights, problem rates, etc.) are clearly marked at the top of both files and are easy to modify.
Output
The generator creates:

blood_bank_data/blood_bank_data.xlsx — all tables in one Excel file
Separate .csv files for each table (donors.csv, donations.csv, etc.)

Author
Created by Anna
License
MIT License — feel free to use, modify, and distribute.
