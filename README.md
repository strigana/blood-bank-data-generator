# blood-bank-data-generator
Synthetic data generator for blood bank analytics (donors, donations, tests, issues etc.)

# Blood Bank Synthetic Data Generator

A realistic synthetic data generator for a national blood bank system.  
Perfect for data analysis, visualization, BI dashboards, quality control demonstrations, and machine learning experiments.

**All data is completely fictional** — no real donors or personal information is used.

## Features

- Generates ~3000 donors and 10,000 donations
- Includes realistic seasonality and day-of-week patterns
- Different error rates for "flagged" specialists
- Realistic blood group distributions with ethnic bias
- Infection screening with true/false positives
- Extended antigen typing
- Donor questionnaire with deferral logic
- Turnaround Time (TAT) simulation for lab tests
- Sample quality issues (hemolysis, lipemia, mislabeling, etc.)

### Generated Tables

| Table                | Description                          |
|----------------------|--------------------------------------|
| donors               | Donor profiles and eligibility       |
| donations            | Donation records                     |
| specialists          | Blood collection staff               |
| collection_sites     | Permanent, mobile and periodic sites |
| sample_issues        | Quality problems with samples        |
| test_results         | Lab TAT (blood group, infections, antigens) |
| infections           | Infectious disease screening results |
| antigen_results      | Extended red cell antigen typing     |
| questionnaire        | Donor screening questionnaire        |

Output is saved to the `blood_bank_data/` folder as both **Excel** (all tables in one file) and individual **CSV** files.

## Installation & Usage

```bash
# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/blood-bank-data-generator.git
cd blood-bank-data-generator

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the generator
python blood_bank_data_generator.py
