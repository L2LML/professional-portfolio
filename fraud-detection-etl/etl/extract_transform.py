import pandas as pd
import numpy as np
from sqlalchemy import create_engine

#__EXTRACT___________________________________________
df = pd.read_csv("../data/fraud_oracle_copy.csv")

print(f"Rows: {len(df)}")
print(f"Columns: {len(df.columns)}")
print(df.head())
print(df.dtypes)

"""cd ~/Projects/professional-portfolio/fraud-detection-etl/etl
python3 extract_transform.py"""

"""Month                   object
WeekOfMonth              int64
DayOfWeek               object
Make                    object
AccidentArea            object
DayOfWeekClaimed        object
MonthClaimed            object
WeekOfMonthClaimed       int64
Sex                     object
MaritalStatus           object
Age                      int64
Fault                   object
PolicyType              object
VehicleCategory         object
VehiclePrice            object
FraudFound_P             int64
PolicyNumber             int64
RepNumber                int64
Deductible               int64
DriverRating             int64
Days_Policy_Accident    object
Days_Policy_Claim       object
PastNumberOfClaims      object
AgeOfVehicle            object
AgeOfPolicyHolder       object
PoliceReportFiled       object
WitnessPresent          object
AgentType               object
NumberOfSuppliments     object
AddressChange_Claim     object
NumberOfCars            object
Year                     int64
BasePolicy              object
dtype: object"""

#___TRANSFORM_______________________________________________
# 1. Lowercase all column names
df.columns = df.columns.str.lower().str.replace(" ", "_")

# 2. Add readable fraud label
df["fraud_label"] = df["fraudfound_p"].apply(lambda x: "Fraud" if x == 1 else "No Fraud")

# 3. Clean VehiclePrice - convert ranges to numeric midpoints
price_map = {
    "less than 20000":  15000,
    "20000 to 29000":   24500,
    "30000 to 39000":   34500,
    "40000 to 59000":   49500,
    "60000 to 69000":   64500,
    "more than 69000":  80000,
}
df["vehicle_price_clean"] = df["vehicleprice"].map(price_map)

# 4. Clean Days_Policy_Accident
days_map = {
    "none":         0,
    "1 to 7":       4,
    "8 to 15":      11,
    "15 to 30":     22,
    "more than 30": 45,
}
df["days_policy_accident_clean"] = df["days_policy_accident"].map(days_map)

# 5. Clean Days_Policy_Claim
df["days_policy_claim_clean"] = df["days_policy_claim"].map(days_map)

print("\n- Transform complete -")
print(df[["vehicleprice", "vehicle_price_clean", "days_policy_accident",
"days_policy_accident_clean"]].head(10))
print(f"\nFraud cases: {df['fraudfound_p'].sum()}")
print(f"Fraud rate: {df['fraudfound_p'].mean()*100:.1f}%")

#_____LOAD____________________________________________________________
engine = create_engine("postgresql+psycopg2://lisamlewandowski@localhost:5432/insurance_claims")

df.to_sql(
    name="fraud_claims",
    con=engine,
    if_exists="replace",
    index=False,
)

print(f"\nloaded {len(df)} rows intoPostgresSQL table: fraud_claims")

# Tableau Public can't connect to Postgres directly, so export a flat file too
df.to_csv("../dashboard/fraud_claims_clean.csv", index=False)
print(f"exported cleaned data to dashboard/fraud_claims_clean.csv")
