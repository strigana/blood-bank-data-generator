"""
Blood Bank Synthetic Data Generator
=====================================
Generates a realistic synthetic dataset for a national blood bank system.
Designed for data analysis, visualization, and QC demonstration purposes.

This generator is region-agnostic and can be adapted to any country.
All names, IDs, and values are entirely fictional.

Output:
    blood_bank_data/
    ├── blood_bank_data.xlsx   (all tables as sheets)
    ├── donors.csv
    ├── donations.csv
    ├── specialists.csv
    ├── collection_sites.csv
    ├── sample_issues.csv
    ├── test_results.csv
    ├── infections.csv
    ├── antigen_results.csv
    └── questionnaire.csv

Usage:
    python generate_blood_bank_data.py

Requirements:
    pip install pandas numpy openpyxl faker

Author: [Your Name]
GitHub: [Your GitHub]
"""

import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
import os

# ============================================================
# RANDOM SEED — ensures reproducibility
# ============================================================
np.random.seed(42)
random.seed(42)

# ============================================================
# CONFIGURATION — adjust parameters here
# ============================================================

N_DONATIONS   = 10_000
N_DONORS      = 3_000
N_SPECIALISTS = 500

DATE_START = datetime(2024, 1, 1)
DATE_END   = datetime(2024, 12, 31)

# Region distribution (must sum to 1.0)
REGION_WEIGHTS = {
    "Central": 0.40,
    "North":   0.25,
    "South":   0.20,
    "East":    0.10,
    "West":    0.05,
}

# Blood group distribution (approximate global average)
BLOOD_GROUP_WEIGHTS = {
    "O+":  0.38, "O-":  0.07,
    "A+":  0.27, "A-":  0.06,
    "B+":  0.15, "B-":  0.02,
    "AB+": 0.04, "AB-": 0.01,
}

# Real population blood group distribution for comparison in analysis
POPULATION_BLOOD_GROUP_PCT = {
    "O+":  38.0, "O-":  7.0,
    "A+":  27.0, "A-":  6.0,
    "B+":  15.0, "B-":  2.0,
    "AB+":  4.0, "AB-": 1.0,
}

# Sample problem rates (per donation, baseline for average specialist)
PROBLEM_RATES = {
    "lipemia":                    0.030,  # donor-caused
    "hemolysis":                  0.015,  # specialist-caused
    "empty_or_insufficient_tube": 0.020,  # specialist-caused
    "missing_barcode":            0.018,  # specialist-caused
    "clotted":                    0.010,  # specialist/transport
    "mislabeled":                 0.008,  # specialist-caused
    "expired_tube":               0.005,  # logistics
    "temperature_deviation":      0.007,  # transport
}

# Multipliers for flagged (problematic) specialists
BAD_SPECIALIST_MULTIPLIER = {
    "hemolysis":                  5.0,
    "empty_or_insufficient_tube": 8.0,
    "missing_barcode":            6.0,
    "mislabeled":                 4.0,
}

# Monthly donation weights (seasonality)
MONTHLY_WEIGHTS = {
    1:  0.90,  2:  1.00,  3:  1.15,  4:  1.15,
    5:  1.05,  6:  0.95,  7:  0.75,  8:  0.75,
    9:  1.10,  10: 1.05,  11: 1.00,  12: 0.85,
}

# Day of week weights — standard Mon-Fri work week
# 0=Mon, 1=Tue, 2=Wed, 3=Thu, 4=Fri, 5=Sat, 6=Sun
DAY_WEIGHTS = {
    0: 1.00, 1: 1.00, 2: 1.00, 3: 1.00,
    4: 0.80, 5: 0.10, 6: 0.10,
}

# ============================================================
# TAT CONFIGURATION (minutes)
# ============================================================
TAT_BLOOD_GROUP     = {"mean": 45,  "std": 15, "min": 20, "max": 180}
TAT_SLOW_RATE       = 0.08
TAT_SLOW_MULTIPLIER = {"mean": 3.0, "std": 0.5}
TAT_INFECTIONS      = {"mean": 120, "std": 30, "min": 60, "max": 480}
TAT_ANTIGENS        = {"mean": 90,  "std": 20, "min": 40, "max": 300}

# ============================================================
# INFECTION RATES
# ============================================================
INFECTION_RATES = {
    "HBsAg":     0.003,
    "Anti_HCV":  0.002,
    "Anti_HIV":  0.001,
    "TPHA":      0.004,
    "Anti_HTLV": 0.001,
    "WNV":       0.002,
}

FALSE_POSITIVE_RATES = {
    "HBsAg":     0.005,
    "Anti_HCV":  0.008,
    "Anti_HIV":  0.003,
    "TPHA":      0.010,
    "Anti_HTLV": 0.004,
    "WNV":       0.006,
}

# ============================================================
# ETHNICITY CONFIGURATION
# ============================================================
ETHNICITY_WEIGHTS = {
    "Caucasian":                0.40,
    "Hispanic":                 0.20,
    "African/African-American": 0.15,
    "Asian":                    0.12,
    "Middle Eastern":           0.08,
    "Other":                    0.05,
}

ETHNICITY_BLOOD_GROUP_BIAS = {
    "Caucasian":                {"O+": 0.37, "A+": 0.33, "B+": 0.12, "AB+": 0.04,
                                 "O-": 0.08, "A-": 0.07, "B-": 0.02, "AB-": 0.01},
    "Hispanic":                 {"O+": 0.53, "A+": 0.29, "B+": 0.09, "AB+": 0.02,
                                 "O-": 0.04, "A-": 0.02, "B-": 0.01, "AB-": 0.00},
    "African/African-American": {"O+": 0.47, "A+": 0.24, "B+": 0.18, "AB+": 0.04,
                                 "O-": 0.04, "A-": 0.02, "B-": 0.01, "AB-": 0.00},
    "Asian":                    {"O+": 0.40, "A+": 0.28, "B+": 0.25, "AB+": 0.05,
                                 "O-": 0.01, "A-": 0.01, "B-": 0.00, "AB-": 0.00},
    "Middle Eastern":           {"O+": 0.38, "A+": 0.30, "B+": 0.18, "AB+": 0.06,
                                 "O-": 0.04, "A-": 0.02, "B-": 0.01, "AB-": 0.01},
    "Other":                    {"O+": 0.38, "A+": 0.27, "B+": 0.17, "AB+": 0.04,
                                 "O-": 0.07, "A-": 0.04, "B-": 0.02, "AB-": 0.01},
}

# ============================================================
# HELPER DATA
# ============================================================
FIRST_NAMES = [
    "James", "Sarah", "Michael", "Emily", "David", "Rachel", "Daniel", "Hannah",
    "Jonathan", "Rebecca", "Matthew", "Leah", "Andrew", "Miriam", "Joshua", "Naomi",
    "Benjamin", "Ruth", "Samuel", "Esther", "Noah", "Abigail", "Ethan", "Judith",
    "Alexander", "Sofia", "William", "Valentina", "Oliver", "Anastasia", "Liam",
    "Natalia", "Lucas", "Tatiana", "Gabriel", "Marina", "Rafael", "Elena", "Leon",
    "Anna", "Mohamed", "Fatima", "Ali", "Layla", "Omar", "Nour", "Yusuf", "Amina",
    "Carlos", "Maria", "Luis", "Isabella", "Jorge", "Diego", "Lucia",
    "Wei", "Mei", "Chen", "Lin", "Yuki", "Hana", "Kenji", "Aiko",
]

LAST_NAMES = [
    "Cohen", "Levi", "Mizrahi", "Peretz", "Shapiro", "Katz", "Friedman",
    "Brown", "Smith", "Johnson", "Williams", "Jones", "Davis", "Wilson", "Taylor",
    "Ivanov", "Petrov", "Smirnov", "Volkov", "Sokolov", "Popov",
    "Hassan", "Ibrahim", "Ali", "Ahmed", "Khalil", "Mansour", "Nasser",
    "Garcia", "Martinez", "Rodriguez", "Lopez", "Hernandez", "Gonzalez",
    "Tanaka", "Yamamoto", "Nakamura", "Suzuki", "Sato", "Watanabe",
    "Miller", "Fischer", "Weiss", "Stern", "Hoffman", "Goldberg", "Klein",
]

COLLECTION_SITE_NAMES_PERMANENT = [
    "Central Blood Center", "University Medical Campus", "City Hospital Donor Unit",
    "Regional Health Hub", "National Donor Center", "Community Medical Center",
    "General Hospital Blood Bank", "Public Health Institute", "Metro Donor Clinic",
]

COLLECTION_SITE_NAMES_MOBILE = [
    "Mobile Unit", "Bloodmobile", "Community Drive", "Neighborhood Bus", "Field Unit",
]

COLLECTION_SITE_NAMES_PERIODIC = [
    "Military Base", "University Campus", "Industrial Zone", "Shopping Mall",
    "Government Office", "Tech Park", "Sports Arena", "Community Center",
    "Corporate Office", "Fire Station", "Police Headquarters",
]

DONATION_TYPES        = ["Whole Blood", "Platelets", "Plasma"]
DONATION_TYPE_WEIGHTS = [0.75, 0.15, 0.10]
SITE_TYPE_COUNTS      = {"permanent": 80, "mobile": 250, "periodic": 170}
GENDERS               = ["Male", "Female"]
MEDICAL_CONDITIONS    = [
    None, None, None, None, None, None, None,
    "Hypertension", "Diabetes", "Asthma", "Anemia (past)", "Thyroid disorder",
]

ANTIGEN_FREQUENCIES = {
    "C":   0.68, "c":   0.80, "E":   0.29, "e":   0.98,
    "K":   0.09, "k":   0.99,
    "Fya": 0.66, "Fyb": 0.83,
    "Jka": 0.77, "Jkb": 0.72,
    "S":   0.55, "s":   0.89,
    "M":   0.78, "N":   0.72,
}

ANTIGEN_ETHNICITY_BIAS = {
    "African/African-American": {"Fya": 0.10, "Fyb": 0.22, "S": 0.30},
    "Middle Eastern":           {"K":   0.06, "E":   0.20},
}

# ============================================================
# TABLE 1: COLLECTION SITES
# ============================================================
print("Generating collection sites...")

sites   = []
site_id = 1
regions = list(REGION_WEIGHTS.keys())

for site_type, count in SITE_TYPE_COUNTS.items():
    for _ in range(count):
        region = random.choices(regions, weights=list(REGION_WEIGHTS.values()))[0]
        if site_type == "permanent":
            name = random.choice(COLLECTION_SITE_NAMES_PERMANENT)
        elif site_type == "mobile":
            name = random.choice(COLLECTION_SITE_NAMES_MOBILE) + f" #{random.randint(1,99):02d}"
        else:
            name = random.choice(COLLECTION_SITE_NAMES_PERIODIC) + f" — {region}"

        sites.append({
            "site_id":         site_id,
            "site_name":       name,
            "site_type":       site_type,
            "region":          region,
            "is_active":       random.choices([True, False], weights=[0.92, 0.08])[0],
            "visits_per_year": (
                365 if site_type == "permanent"
                else random.randint(20, 100) if site_type == "mobile"
                else random.randint(4, 24)
            ),
        })
        site_id += 1

sites_df = pd.DataFrame(sites)
print(f"  -> {len(sites_df):,} collection sites created")

# ============================================================
# TABLE 2: SPECIALISTS
# ============================================================
print("Generating specialists...")

bad_specialist_ids = random.sample(range(1, N_SPECIALISTS + 1), 3)
specialists = []

for i in range(1, N_SPECIALISTS + 1):
    experience = random.randint(1, 25)
    specialists.append({
        "specialist_id":    i,
        "full_name":        f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}",
        "region":           random.choices(regions, weights=list(REGION_WEIGHTS.values()))[0],
        "years_experience": experience,
        "seniority":        ("junior" if experience <= 3 else
                             "mid"    if experience <= 10 else "senior"),
        "is_flagged":       i in bad_specialist_ids,
    })

specialists_df = pd.DataFrame(specialists)
print(f"  -> {len(specialists_df):,} specialists created")
print(f"  -> Flagged IDs: {bad_specialist_ids}")
print(f"     Names: {[specialists_df.loc[specialists_df.specialist_id==s,'full_name'].values[0] for s in bad_specialist_ids]}")

# ============================================================
# TABLE 3: DONORS
# ============================================================
print("Generating donors...")

donors = []
for i in range(1, N_DONORS + 1):
    gender     = random.choice(GENDERS)
    age        = random.randint(18, 65)
    weight     = round(random.uniform(50, 110), 1)
    hemoglobin = round(random.gauss(13.8 if gender == "Female" else 15.2, 1.2), 1)
    hemoglobin = max(9.0, min(20.0, hemoglobin))
    medical    = random.choice(MEDICAL_CONDITIONS)
    eligible   = (18 <= age <= 65 and weight >= 50
                  and hemoglobin >= (12.5 if gender == "Female" else 13.0)
                  and medical is None)
    region    = random.choices(regions, weights=list(REGION_WEIGHTS.values()))[0]
    ethnicity = random.choices(
        list(ETHNICITY_WEIGHTS.keys()),
        weights=list(ETHNICITY_WEIGHTS.values())
    )[0]

    donors.append({
        "donor_id":    f"DNR{i:06d}",
        "national_id": str(random.randint(100_000_000, 999_999_999)),
        "full_name":   f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}",
        "gender":      gender,
        "age":         age,
        "blood_group": random.choices(
            list(ETHNICITY_BLOOD_GROUP_BIAS[ethnicity].keys()),
            weights=list(ETHNICITY_BLOOD_GROUP_BIAS[ethnicity].values())
        )[0],
        "region":      region,
        "ethnicity":   ethnicity,
        "weight_kg":   weight,
        "hemoglobin_g_dL":       hemoglobin,
        "medical_condition":     medical,
        "eligible_for_donation": eligible,
        "is_repeat_donor": random.choices([True, False], weights=[0.60, 0.40])[0],
        "registration_date": DATE_START - timedelta(days=random.randint(0, 1825)),
        "total_lifetime_donations": int(np.random.exponential(scale=4)) + 1,
    })

donors_df = pd.DataFrame(donors)
print(f"  -> {len(donors_df):,} donors created")

# ============================================================
# TABLE 4: DONATIONS
# ============================================================
print("Generating donations...")

active_sites          = sites_df[sites_df.is_active].copy()
region_specialist_ids = {
    r: specialists_df[specialists_df.region == r]["specialist_id"].tolist()
    for r in regions
}

donations = []
for i in range(1, N_DONATIONS + 1):
    region       = random.choices(regions, weights=list(REGION_WEIGHTS.values()))[0]
    region_sites = active_sites[active_sites.region == region]
    site         = region_sites.sample(1).iloc[0]

    spec_pool = region_specialist_ids.get(region, specialists_df["specialist_id"].tolist())
    if not spec_pool:
        spec_pool = specialists_df["specialist_id"].tolist()
    specialist_id = random.choice(spec_pool)

    eligible_donors = donors_df[(donors_df.region == region) & donors_df.eligible_for_donation]
    if len(eligible_donors) == 0:
        eligible_donors = donors_df[donors_df.eligible_for_donation]
    donor = eligible_donors.sample(1).iloc[0]

    # Seasonality-weighted date
    month       = random.choices(list(MONTHLY_WEIGHTS.keys()),
                                 weights=list(MONTHLY_WEIGHTS.values()))[0]
    month_start = DATE_START.replace(month=month)
    month_end   = (DATE_START.replace(year=DATE_START.year + 1, month=1)
                   if month == 12 else DATE_START.replace(month=month + 1))
    days_in_month = (month_end - month_start).days

    for _ in range(20):
        day_offset = random.randint(0, days_in_month - 1)
        candidate  = month_start + timedelta(days=day_offset)
        if random.random() < DAY_WEIGHTS[candidate.weekday()]:
            date = candidate
            break
    else:
        date = candidate

    donations.append({
        "donation_id":     f"DON{i:07d}",
        "donor_id":        donor["donor_id"],
        "blood_group":     donor["blood_group"],
        "region":          region,
        "site_id":         site["site_id"],
        "site_type":       site["site_type"],
        "specialist_id":   specialist_id,
        "donation_type":   random.choices(DONATION_TYPES, weights=DONATION_TYPE_WEIGHTS)[0],
        "donation_date":   date,
        "donation_status": random.choices(
            ["completed", "deferred", "abandoned"],
            weights=[0.88, 0.09, 0.03]
        )[0],
    })

donations_df = pd.DataFrame(donations)
print(f"  -> {len(donations_df):,} donations created")

# ============================================================
# TABLE 5: SAMPLE ISSUES
# ============================================================
print("Generating sample issues...")

SPECIALIST_CAUSED = {
    "hemolysis", "empty_or_insufficient_tube", "missing_barcode", "mislabeled"
}
issues    = []
completed = donations_df[donations_df.donation_status == "completed"]

for _, don in completed.iterrows():
    spec_id = don["specialist_id"]
    is_bad  = spec_id in bad_specialist_ids

    for problem, base_rate in PROBLEM_RATES.items():
        rate = (base_rate * BAD_SPECIALIST_MULTIPLIER.get(problem, 1.0)
                if is_bad and problem in SPECIALIST_CAUSED else base_rate)
        if random.random() < rate:
            issues.append({
                "issue_id":      f"ISS{len(issues)+1:06d}",
                "donation_id":   don["donation_id"],
                "specialist_id": spec_id,
                "region":        don["region"],
                "site_type":     don["site_type"],
                "donation_date": don["donation_date"],
                "issue_type":    problem,
                "caused_by": (
                    "donor"      if problem == "lipemia"
                    else "logistics" if problem in ("expired_tube", "temperature_deviation")
                    else "specialist"
                ),
            })

issues_df = pd.DataFrame(issues)
print(f"  -> {len(issues_df):,} sample issues generated")

# ============================================================
# TABLE 6: TEST RESULTS (TAT)
# ============================================================
print("Generating test results (TAT)...")

def generate_tat(config, is_slow=False):
    mult    = (max(1.5, random.gauss(TAT_SLOW_MULTIPLIER["mean"],
                                      TAT_SLOW_MULTIPLIER["std"]))
               if is_slow else 1.0)
    minutes = random.gauss(config["mean"] * mult, config["std"])
    return int(max(config["min"], min(config["max"], minutes)))

test_results = []
for _, don in completed.iterrows():
    received_at = pd.Timestamp(don["donation_date"]) + timedelta(
        hours=random.randint(0, 4), minutes=random.randint(0, 59)
    )
    is_slow = random.random() < TAT_SLOW_RATE
    bg_tat  = generate_tat(TAT_BLOOD_GROUP, is_slow)
    inf_tat = generate_tat(TAT_INFECTIONS)
    ant_tat = generate_tat(TAT_ANTIGENS)

    test_results.append({
        "donation_id":           don["donation_id"],
        "specialist_id":         don["specialist_id"],
        "region":                don["region"],
        "sample_received_at":    received_at,
        "blood_group_result_at": received_at + timedelta(minutes=bg_tat),
        "blood_group_tat_min":   bg_tat,
        "is_slow_sample":        is_slow,
        "infection_result_at":   received_at + timedelta(minutes=inf_tat),
        "infection_tat_min":     inf_tat,
        "antigen_result_at":     received_at + timedelta(minutes=ant_tat),
        "antigen_tat_min":       ant_tat,
        "total_tat_min":         max(bg_tat, inf_tat, ant_tat),
    })

test_results_df = pd.DataFrame(test_results)
print(f"  -> {len(test_results_df):,} test result records")
print(f"  -> Slow samples: {test_results_df['is_slow_sample'].sum():,} "
      f"({test_results_df['is_slow_sample'].mean()*100:.1f}%)")

# ============================================================
# TABLE 7: INFECTION RESULTS
# ============================================================
print("Generating infection screening results...")

infection_records = []
for _, don in completed.iterrows():
    month     = pd.Timestamp(don["donation_date"]).month
    wnv_boost = 2.5 if month in [6, 7, 8, 9] else 0.3

    for infection, base_rate in INFECTION_RATES.items():
        rate           = base_rate * wnv_boost if infection == "WNV" else base_rate
        true_positive  = random.random() < rate
        false_positive = (not true_positive) and (random.random() < FALSE_POSITIVE_RATES[infection])
        reactive       = true_positive or false_positive

        infection_records.append({
            "donation_id":   don["donation_id"],
            "donor_id":      don["donor_id"],
            "region":        don["region"],
            "donation_date": don["donation_date"],
            "infection":     infection,
            "result":        "reactive" if reactive else "non-reactive",
            "confirmed":     true_positive,
            "false_positive": false_positive,
        })

infection_df = pd.DataFrame(infection_records)
print(f"  -> {len(infection_df):,} infection test records")
print(f"  -> Confirmed positive: {infection_df[infection_df.confirmed].shape[0]:,}")
print(f"  -> False positive:     {infection_df[infection_df.false_positive].shape[0]:,}")

# ============================================================
# TABLE 8: ANTIGEN RESULTS
# ============================================================
print("Generating antigen typing results...")

antigen_records = []
for _, don in completed.iterrows():
    donor_row = donors_df[donors_df.donor_id == don["donor_id"]]
    if len(donor_row) == 0:
        continue
    ethnicity = donor_row.iloc[0]["ethnicity"]
    antigens  = {
        ag: ("+" if random.random() <
             ANTIGEN_ETHNICITY_BIAS.get(ethnicity, {}).get(ag, freq) else "-")
        for ag, freq in ANTIGEN_FREQUENCIES.items()
    }
    record = {
        "donation_id": don["donation_id"],
        "donor_id":    don["donor_id"],
        "region":      don["region"],
        "ethnicity":   ethnicity,
        "blood_group": don["blood_group"],
    }
    record.update(antigens)
    antigen_records.append(record)

antigen_df = pd.DataFrame(antigen_records)
print(f"  -> {len(antigen_df):,} antigen typing records")

# ============================================================
# TABLE 9: DONOR QUESTIONNAIRE
# ============================================================
print("Generating donor questionnaires...")

questionnaires = []
for _, don in completed.iterrows():
    donor_row = donors_df[donors_df.donor_id == don["donor_id"]]
    if len(donor_row) == 0:
        continue
    donor = donor_row.iloc[0]

    travelled       = random.random() < 0.15
    recent_illness  = random.random() < 0.08
    medications     = random.random() < 0.12
    tattoo_piercing = random.random() < 0.07
    high_risk       = random.random() < 0.02
    recent_surgery  = random.random() < 0.03
    pregnancy       = (donor["gender"] == "Female") and (random.random() < 0.04)
    low_hemoglobin  = donor["hemoglobin_g_dL"] < (
        12.5 if donor["gender"] == "Female" else 13.0
    )
    complete = random.random() > 0.03
    deferred = any([
        recent_illness, high_risk, tattoo_piercing,
        pregnancy, low_hemoglobin, recent_surgery,
        medications and random.random() < 0.3,
        travelled   and random.random() < 0.2,
    ])

    questionnaires.append({
        "donation_id":            don["donation_id"],
        "donor_id":               don["donor_id"],
        "region":                 don["region"],
        "donation_date":          don["donation_date"],
        "travelled_abroad_3m":    travelled,
        "recent_illness":         recent_illness,
        "medications":            medications,
        "tattoo_piercing_6m":     tattoo_piercing,
        "high_risk_behavior":     high_risk,
        "recent_surgery":         recent_surgery,
        "pregnancy":              pregnancy,
        "low_hemoglobin_flag":    low_hemoglobin,
        "questionnaire_complete": complete,
        "deferred":               deferred,
        "deferral_reason": (
            "low_hemoglobin" if low_hemoglobin
            else "pregnancy"   if pregnancy
            else "high_risk"   if high_risk
            else "illness"     if recent_illness
            else "surgery"     if recent_surgery
            else "tattoo"      if tattoo_piercing
            else "travel"      if travelled   and random.random() < 0.2
            else "medications" if medications and random.random() < 0.3
            else None
        ),
    })

questionnaire_df = pd.DataFrame(questionnaires)
print(f"  -> {len(questionnaire_df):,} questionnaire records")
print(f"  -> Deferred: {questionnaire_df['deferred'].sum():,} "
      f"({questionnaire_df['deferred'].mean()*100:.1f}%)")

# ============================================================
# SAVE ALL TABLES
# ============================================================
print("\nSaving to Excel and CSV...")

output_dir = "blood_bank_data"
os.makedirs(output_dir, exist_ok=True)

with pd.ExcelWriter(os.path.join(output_dir, "blood_bank_data.xlsx"),
                    engine="openpyxl") as writer:
    donors_df.to_excel(writer,        sheet_name="donors",           index=False)
    donations_df.to_excel(writer,     sheet_name="donations",        index=False)
    specialists_df.to_excel(writer,   sheet_name="specialists",      index=False)
    sites_df.to_excel(writer,         sheet_name="collection_sites", index=False)
    issues_df.to_excel(writer,        sheet_name="sample_issues",    index=False)
    test_results_df.to_excel(writer,  sheet_name="test_results",     index=False)
    infection_df.to_excel(writer,     sheet_name="infections",       index=False)
    antigen_df.to_excel(writer,       sheet_name="antigen_results",  index=False)
    questionnaire_df.to_excel(writer, sheet_name="questionnaire",    index=False)

for df, name in [
    (donors_df,        "donors"),
    (donations_df,     "donations"),
    (specialists_df,   "specialists"),
    (sites_df,         "collection_sites"),
    (issues_df,        "sample_issues"),
    (test_results_df,  "test_results"),
    (infection_df,     "infections"),
    (antigen_df,       "antigen_results"),
    (questionnaire_df, "questionnaire"),
]:
    df.to_csv(os.path.join(output_dir, f"{name}.csv"), index=False)

# ============================================================
# SUMMARY
# ============================================================
print("\n" + "=" * 57)
print("  BLOOD BANK DATABASE — GENERATION COMPLETE")
print("=" * 57)
print(f"  Donors:            {len(donors_df):>8,}")
print(f"  Donations:         {len(donations_df):>8,}")
print(f"  Specialists:       {len(specialists_df):>8,}")
print(f"  Collection sites:  {len(sites_df):>8,}")
print(f"  Sample issues:     {len(issues_df):>8,}")
print(f"  Test results:      {len(test_results_df):>8,}")
print(f"  Infection records: {len(infection_df):>8,}")
print(f"  Antigen records:   {len(antigen_df):>8,}")
print(f"  Questionnaires:    {len(questionnaire_df):>8,}")
print("=" * 57)
print(f"\n  Flagged specialists (high error rate):")
for sid in bad_specialist_ids:
    name  = specialists_df.loc[specialists_df.specialist_id == sid, "full_name"].values[0]
    count = issues_df[issues_df.specialist_id == sid].shape[0]
    print(f"    ID {sid:>3} | {name:<28} | {count:>4} issues")
print(f"\n  Issue breakdown:")
print(issues_df.groupby(["issue_type", "caused_by"]).size().rename("count").to_string())
print(f"\n  Output saved to: ./{output_dir}/")
print("=" * 57)