from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import joblib

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

model         = joblib.load("lightgbm_model.pkl")
model_columns = joblib.load("model_columns.pkl")

def safe_float(value):
    try:
        return float(value)
    except:
        return 0.0

@app.post("/risk-score")
def get_risk_score(payload: dict):

    data = payload.get("data", {})

    # ── Raw inputs ────────────────────────────────────────────
    income         = safe_float(data.get("income"))
    loan_amount    = safe_float(data.get("loan_amount"))
    credit_score   = safe_float(data.get("Credit_Score"))
    property_value = safe_float(data.get("property_value"))
    ltv            = safe_float(data.get("LTV"))
    dtir1          = safe_float(data.get("dtir1"))

    # ── Feature Engineering — exactly as notebook cell 63 ────
    loan_income_ratio   = loan_amount  / (income         + 1)
    loan_property_ratio = loan_amount  / (property_value + 1)
    LTV_dti_interaction = ltv          *  dtir1
    credit_income_ratio = credit_score / (income         + 1)

    data["loan_income_ratio"]   = loan_income_ratio
    data["loan_property_ratio"] = loan_property_ratio
    data["LTV_dti_interaction"] = LTV_dti_interaction
    data["credit_income_ratio"] = credit_income_ratio

    # ── Build dataframe with exact 46-column order ────────────
    clean = {col: data.get(col, 0) for col in model_columns}
    df    = pd.DataFrame([clean])
    df    = df.apply(pd.to_numeric, errors="coerce").fillna(0)

    # ── CRITICAL FIX ──────────────────────────────────────────
    # LightGBM printed this warning during training:
    #   "Found whitespace in feature_names, replace with underlines"
    # This means LightGBM internally renamed all columns that have spaces
    # to use underscores instead. For example:
    #   "loan_type_Home Loan"  →  "loan_type_Home_Loan"
    #   "loan_purpose_House Purchase"  →  "loan_purpose_House_Purchase"
    #   "application_submission_mode_Branch Visit" → "..._Branch_Visit"
    # When predicting, we MUST rename to match what LightGBM stored internally.
    # Without this, every column with a space is treated as 0 (missing),
    # which is why ALL predictions were coming out as Critical / very high risk.
    df.columns = [col.replace(" ", "_") for col in df.columns]

    # ── Predict ───────────────────────────────────────────────
    prob          = float(model.predict_proba(df)[0][1])
    expected_loss = prob * loan_amount

    # ── Risk tier — same thresholds as notebook cell 101 ─────
    if expected_loss < 50000:
        risk   = "Low"
        action = "Send automated reminder"
    elif expected_loss < 200000:
        risk   = "Medium"
        action = "Contact borrower"
    elif expected_loss < 500000:
        risk   = "High"
        action = "Assign recovery officer"
    else:
        risk   = "Critical"
        action = "Legal escalation"

    # ── Bank decision ─────────────────────────────────────────
    bank_decision = {
        "Low":      "Approve Loan",
        "Medium":   "Approve with Conditions",
        "High":     "Reject / Request Collateral",
        "Critical": "Reject / Legal Escalation",
    }[risk]

    return {
        "risk_level":           risk,
        "default_probability":  round(prob, 4),
        "expected_loss":        round(expected_loss, 2),
        "recommended_action":   action,
        "bank_decision":        bank_decision,
        "loan_income_ratio":    round(loan_income_ratio,   2),
        "loan_property_ratio":  round(loan_property_ratio, 2),
        "LTV_dti_interaction":  round(LTV_dti_interaction, 2),
        "credit_income_ratio":  round(credit_income_ratio, 6),
    }