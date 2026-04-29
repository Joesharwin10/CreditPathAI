import streamlit as st
import pandas as pd
import joblib
import plotly.graph_objects as go

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="CreditPath AI",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Custom CSS — dark theme matching original React app ───────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background-color: #0b1220;
    color: #f1f5f9;
}

/* Hide default Streamlit elements */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2rem 2rem 4rem; max-width: 1400px; }

/* ── App header ── */
.app-header {
    margin-bottom: 0.5rem;
}
.app-title {
    font-size: 2rem;
    font-weight: 700;
    margin: 0;
    color: #f1f5f9;
}
.app-subtitle {
    color: #9ca3af;
    font-size: 0.95rem;
    margin-top: 0.2rem;
}

/* ── Section labels ── */
.section-label {
    font-size: 11px;
    font-weight: 700;
    color: #60a5fa;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    border-bottom: 1px solid #1f2937;
    padding-bottom: 6px;
    margin-top: 1.2rem;
    margin-bottom: 0.5rem;
}
.bank-section-label {
    color: #f59e0b;
    border-bottom-color: #f59e0b44;
}

/* ── Cards ── */
.result-card {
    background: #111827;
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1rem;
}

/* ── Risk badge ── */
.risk-badge {
    border-radius: 10px;
    padding: 1.2rem 1.5rem;
    margin: 1rem 0;
    line-height: 2.2;
    background: #1f2937;
    border: 2px solid;
}
.risk-title {
    font-size: 1.8rem;
    font-weight: 700;
}

/* ── KPI cards ── */
.kpi-row {
    display: flex;
    gap: 12px;
    flex-wrap: wrap;
    margin-bottom: 1rem;
}
.kpi-card {
    background: #111827;
    border-radius: 10px;
    padding: 14px 18px;
    flex: 1;
    min-width: 120px;
}
.kpi-label {
    font-size: 10px;
    color: #9ca3af;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}
.kpi-value {
    font-size: 1.15rem;
    font-weight: 700;
    margin-top: 4px;
}

/* ── Recommendation box ── */
.recommendation {
    background: #1f2937;
    border-radius: 8px;
    padding: 14px 16px;
    margin: 12px 0;
    line-height: 1.7;
    border-left: 4px solid;
}
.rec-title { font-weight: 600; margin-bottom: 6px; }
.rec-text  { color: #d1d5db; font-size: 0.9rem; }

/* ── Feature table ── */
.fe-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 13px;
    margin-top: 0.5rem;
}
.fe-table th {
    background: #1f2937;
    padding: 8px 10px;
    text-align: left;
    color: #9ca3af;
    font-weight: 600;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}
.fe-table td {
    padding: 8px 10px;
    border-bottom: 1px solid #1f2937;
    font-size: 13px;
}
.fe-formula {
    color: #60a5fa;
    font-size: 11px;
    font-family: monospace;
}

/* ── Home cards ── */
.home-card {
    background: #111827;
    border: 2px solid #1f2937;
    border-radius: 16px;
    padding: 2.2rem 2rem;
    cursor: pointer;
    transition: border-color 0.2s;
    text-align: left;
    margin-bottom: 1rem;
}
.home-icon { font-size: 2.2rem; margin-bottom: 0.6rem; }
.home-card h3 { margin: 0 0 0.6rem; font-size: 1.3rem; }
.home-card p  { color: #9ca3af; font-size: 0.9rem; line-height: 1.6; margin-bottom: 1.2rem; }
.home-badge {
    display: inline-block;
    background: #2563eb;
    color: white;
    padding: 8px 18px;
    border-radius: 8px;
    font-size: 13px;
    font-weight: 600;
}

/* ── Submitted banner ── */
.submitted-banner {
    background: #14532d;
    border: 1px solid #22c55e;
    border-radius: 8px;
    padding: 10px 14px;
    font-size: 13px;
    color: #86efac;
    margin-bottom: 1rem;
}

/* ── Applicant summary table ── */
.summary-table { width: 100%; border-collapse: collapse; font-size: 13px; }
.summary-table tr { border-bottom: 1px solid #1f2937; }
.summary-table tr:last-child { border-bottom: none; }
.summary-table td { padding: 7px 4px; }
.summary-table td:first-child { color: #9ca3af; width: 48%; }
.summary-table td:last-child  { color: #e5e7eb; font-weight: 500; }

/* ── Streamlit widget overrides ── */
div[data-testid="stNumberInput"] input,
div[data-testid="stTextInput"] input,
div[data-testid="stSelectbox"] > div > div {
    background-color: #1f2937 !important;
    border: 1px solid #374151 !important;
    color: #f1f5f9 !important;
    border-radius: 6px !important;
}
div[data-testid="stSelectbox"] svg { fill: #9ca3af; }

.stButton > button {
    background: #2563eb;
    color: white;
    border: none;
    border-radius: 8px;
    padding: 0.6rem 1.5rem;
    font-size: 15px;
    font-weight: 600;
    width: 100%;
    cursor: pointer;
}
.stButton > button:hover { background: #1d4ed8; }

div[data-testid="metric-container"] {
    background: #111827;
    border-radius: 10px;
    padding: 12px 16px;
}
div[data-testid="metric-container"] label { color: #9ca3af !important; font-size: 11px !important; }

/* Readonly-style info box */
.readonly-field {
    background: #0f172a;
    border: 1px solid #1e3a5f;
    border-radius: 6px;
    padding: 9px 12px;
    color: #60a5fa;
    font-size: 14px;
    margin-bottom: 12px;
    font-family: monospace;
}

.placeholder-text {
    color: #6b7280;
    line-height: 1.7;
    font-size: 0.95rem;
    padding: 1rem 0;
}

hr.divider {
    border: none;
    border-top: 1px solid #1f2937;
    margin: 1rem 0;
}
</style>
""", unsafe_allow_html=True)

# ── Load model ────────────────────────────────────────────────────────────────
@st.cache_resource
def load_model():
    model   = joblib.load("lightgbm_model.pkl")
    columns = joblib.load("model_columns.pkl")
    return model, columns

model, model_columns = load_model()

# ── Risk helpers ──────────────────────────────────────────────────────────────
RISK_COLOR = {
    "Low":      "#22c55e",
    "Medium":   "#f59e0b",
    "High":     "#ef4444",
    "Critical": "#dc2626",
}

APPLICANT_MSG = {
    "Low":      "Your financial profile looks healthy. You are likely to get loan approval.",
    "Medium":   "Your profile has some risk. Consider reducing the loan amount or improving your repayment history.",
    "High":     "High financial risk detected. Apply for a smaller loan or increase your down payment.",
    "Critical": "Critical risk level. Please consult a financial advisor before proceeding.",
}

BANK_MSG = {
    "Low":      "Low risk borrower. Safe to approve the loan under standard terms.",
    "Medium":   "Moderate risk. Approve with conditions — higher down payment or co-applicant required.",
    "High":     "High risk borrower. Assign a recovery officer and request additional collateral.",
    "Critical": "Critical risk. Legal review required before any approval decision.",
}

SAFE_LIMITS = {"lir": 3.0, "lpr": 4.0}

# ── Inference function — mirrors api.py exactly ───────────────────────────────
def run_inference(data: dict):
    income         = float(data.get("income",         0) or 0)
    loan_amount    = float(data.get("loan_amount",    0) or 0)
    credit_score   = float(data.get("Credit_Score",  0) or 0)
    property_value = float(data.get("property_value",0) or 0)
    ltv            = float(data.get("LTV",            0) or 0)
    dtir1          = float(data.get("dtir1",          0) or 0)

    loan_income_ratio   = loan_amount  / (income         + 1)
    loan_property_ratio = loan_amount  / (property_value + 1)
    LTV_dti_interaction = ltv          *  dtir1
    credit_income_ratio = credit_score / (income         + 1)

    data["loan_income_ratio"]   = loan_income_ratio
    data["loan_property_ratio"] = loan_property_ratio
    data["LTV_dti_interaction"] = LTV_dti_interaction
    data["credit_income_ratio"] = credit_income_ratio

    clean = {col: data.get(col, 0) for col in model_columns}
    df    = pd.DataFrame([clean])
    df    = df.apply(pd.to_numeric, errors="coerce").fillna(0)
    df.columns = [col.replace(" ", "_") for col in df.columns]

    prob          = float(model.predict_proba(df)[0][1])
    expected_loss = prob * loan_amount

    if expected_loss < 50000:
        risk, action = "Low",      "Send automated reminder"
    elif expected_loss < 200000:
        risk, action = "Medium",   "Contact borrower"
    elif expected_loss < 500000:
        risk, action = "High",     "Assign recovery officer"
    else:
        risk, action = "Critical", "Legal escalation"

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
        "loan_income_ratio":    round(loan_income_ratio,   4),
        "loan_property_ratio":  round(loan_property_ratio, 4),
        "LTV_dti_interaction":  round(LTV_dti_interaction, 4),
        "credit_income_ratio":  round(credit_income_ratio, 6),
    }

# ── Session state init ────────────────────────────────────────────────────────
for key, default in {
    "page":                "home",
    "applicant_submitted": False,
    "result":              None,
    "applicant":           {},
    "bank_data":           {},
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# ── Helper: header ────────────────────────────────────────────────────────────
def render_header(show_back=True):
    col1, col2 = st.columns([6, 1])
    with col1:
        st.markdown('<div class="app-header"><p class="app-title">💳 CreditPath AI</p>'
                    '<p class="app-subtitle">AI-Powered Loan Risk Intelligence System</p></div>',
                    unsafe_allow_html=True)
    with col2:
        if show_back:
            if st.button("← Home", key="back_btn"):
                st.session_state.page   = "home"
                st.session_state.result = None
                st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# HOME PAGE
# ══════════════════════════════════════════════════════════════════════════════
def page_home():
    st.markdown('<p class="app-title">💳 CreditPath AI</p>'
                '<p class="app-subtitle">AI-Powered Loan Risk Intelligence System</p>',
                unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("Welcome! Please select who you are to get started.")
    st.markdown("<br>", unsafe_allow_html=True)

    # Style: small blue button flush under each dark card
    st.markdown("""
    <style>
    [data-testid="column"] .stButton > button {
        background: #2563eb !important;
        color: white !important;
        border: none !important;
        border-radius: 0 0 14px 14px !important;
        padding: 10px 20px !important;
        font-size: 14px !important;
        font-weight: 600 !important;
        margin-top: -2px !important;
        width: 100% !important;
    }
    [data-testid="column"] .stButton > button:hover {
        background: #1d4ed8 !important;
    }
    </style>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown("""
        <div style="background:#111827;border:2px solid #1f2937;border-radius:16px;
                    padding:36px 32px 16px 32px;">
            <div style="font-size:2.2rem;margin-bottom:12px;">👤</div>
            <h3 style="margin:0 0 10px;font-size:1.35rem;color:#f1f5f9;">Loan Applicant</h3>
            <p style="color:#9ca3af;font-size:0.93rem;line-height:1.6;margin:0 0 18px;">
                I am applying for a loan. I want to fill my application details
                and see my risk assessment result.
            </p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Start Application →", key="go_user", use_container_width=True):
            st.session_state.page = "user"
            st.rerun()

    with col2:
        st.markdown("""
        <div style="background:#111827;border:2px solid #1f2937;border-radius:16px;
                    padding:36px 32px 16px 32px;">
            <div style="font-size:2.2rem;margin-bottom:12px;">🏦</div>
            <h3 style="margin:0 0 10px;font-size:1.35rem;color:#f1f5f9;">Bank / Institution</h3>
            <p style="color:#9ca3af;font-size:0.93rem;line-height:1.6;margin:0 0 18px;">
                I am a bank staff member. I will review the submitted application,
                enter bank details, and assess the risk.
            </p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Open Dashboard →", key="go_bank", use_container_width=True):
            st.session_state.page = "bank"
            st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# APPLICANT PAGE
# ══════════════════════════════════════════════════════════════════════════════
def page_user():
    render_header()
    st.markdown("<hr class='divider'>", unsafe_allow_html=True)

    col_form, col_result = st.columns(2, gap="large")

    # ── FORM ──────────────────────────────────────────────────────────────────
    with col_form:
        st.markdown("### 👤 Loan Application Form")

        submitted = st.session_state.applicant_submitted
        if submitted:
            st.markdown('<div class="submitted-banner">✅ Application submitted! The bank staff will now review and assess your risk.</div>',
                        unsafe_allow_html=True)

        # ── Personal Details
        st.markdown('<p class="section-label">Personal Details</p>', unsafe_allow_html=True)

        name = st.text_input("Full Name", placeholder="e.g. Arjun Sharma",
                             value=st.session_state.applicant.get("name", ""),
                             disabled=submitted, key="name")
        c1, c2 = st.columns(2)
        with c1:
            age = st.number_input("Age", min_value=18, max_value=80,
                                  value=int(st.session_state.applicant.get("age", 30)),
                                  disabled=submitted, key="age")
        with c2:
            gender = st.selectbox("Gender", ["Male", "Female"],
                                  index=0 if st.session_state.applicant.get("gender","Male")=="Male" else 1,
                                  disabled=submitted, key="gender")

        income = st.number_input("Annual Income (₹)", min_value=0, step=10000,
                                 value=int(st.session_state.applicant.get("income", 0)),
                                 help="Total yearly income before tax. Dataset range: ₹2L–₹20L",
                                 disabled=submitted, key="income")

        occupation_type = st.selectbox("Employment Type",
                                       ["Salaried", "Professional", "Self-Employed", "Business"],
                                       index=["Salaried","Professional","Self-Employed","Business"].index(
                                           st.session_state.applicant.get("occupation_type","Salaried")),
                                       disabled=submitted, key="occupation_type",
                                       help="Salaried=employed | Professional=doctor/lawyer/CA | Self-Employed=own business")

        # ── Loan Details
        st.markdown('<p class="section-label">Loan Details</p>', unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            loan_amount = st.number_input("Loan Amount (₹)", min_value=0, step=10000,
                                          value=int(st.session_state.applicant.get("loan_amount", 0)),
                                          disabled=submitted, key="loan_amount")
        with c2:
            property_value = st.number_input("Property Value (₹)", min_value=0, step=10000,
                                              value=int(st.session_state.applicant.get("property_value", 0)),
                                              disabled=submitted, key="property_value")

        ltv = round((loan_amount / property_value * 100), 2) if property_value > 0 else 0.0
        st.markdown(f'<p style="font-size:13px;color:#9ca3af;margin-bottom:2px;">LTV — Loan to Value Ratio <span style="color:#60a5fa;font-size:11px;">(auto-calculated)</span></p>'
                    f'<div class="readonly-field">{ltv}%</div>', unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            loan_type = st.selectbox("Loan Type",
                                     ["Home Loan", "Education Loan", "Personal Loan", "Business Loan"],
                                     index=["Home Loan","Education Loan","Personal Loan","Business Loan"].index(
                                         st.session_state.applicant.get("loan_type","Home Loan")),
                                     disabled=submitted, key="loan_type")
        with c2:
            loan_purpose = st.selectbox("Loan Purpose",
                                        ["House Purchase", "Education", "Medical", "Debt Consolidation"],
                                        index=["House Purchase","Education","Medical","Debt Consolidation"].index(
                                            st.session_state.applicant.get("loan_purpose","House Purchase")),
                                        disabled=submitted, key="loan_purpose")

        # ── Property & Other Details
        st.markdown('<p class="section-label">Property & Other Details</p>', unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            region = st.selectbox("Region",
                                  ["central", "North-East", "south"],
                                  index=["central","North-East","south"].index(
                                      st.session_state.applicant.get("region","central")),
                                  disabled=submitted, key="region",
                                  help="Region where the property is located")
        with c2:
            occupancy_type = st.selectbox("Occupancy Type",
                                          ["pr", "sr", "ir"],
                                          format_func=lambda x: {"pr":"Primary Residence (pr)",
                                                                   "sr":"Secondary Residence (sr)",
                                                                   "ir":"Investment / Rental (ir)"}[x],
                                          index=["pr","sr","ir"].index(
                                              st.session_state.applicant.get("occupancy_type","pr")),
                                          disabled=submitted, key="occupancy_type")

        c1, c2 = st.columns(2)
        with c1:
            biz_commercial = st.selectbox("Business / Commercial?",
                                          ["nob/c", "b/c"],
                                          format_func=lambda x: "No — Personal Use" if x=="nob/c" else "Yes — Business Use",
                                          disabled=submitted, key="biz_commercial")
        with c2:
            applicant_assurity = st.selectbox("Applicant Assurity",
                                              ["Guarantor", "Property"],
                                              disabled=submitted, key="applicant_assurity",
                                              help="Guarantor=someone vouches | Property=property pledged")

        submission_mode = st.selectbox("Submission Mode",
                                       ["Online", "Branch Visit"],
                                       disabled=submitted, key="submission_mode")

        st.markdown("<br>", unsafe_allow_html=True)

        if not submitted:
            if st.button("Submit Application", key="submit_applicant", use_container_width=True):
                if not name or not income or not loan_amount:
                    st.error("Please fill in at least Name, Income, and Loan Amount.")
                else:
                    st.session_state.applicant = {
                        "name": name, "age": age, "gender": gender,
                        "income": income, "occupation_type": occupation_type,
                        "loan_amount": loan_amount, "property_value": property_value,
                        "loan_type": loan_type, "loan_purpose": loan_purpose,
                        "region": region, "occupancy_type": occupancy_type,
                        "biz_commercial": biz_commercial,
                        "applicant_assurity": applicant_assurity,
                        "submission_mode": submission_mode,
                        "ltv": ltv,
                    }
                    st.session_state.applicant_submitted = True
                    st.session_state.result = None
                    st.rerun()
        else:
            if st.button("✏️ Edit Application", key="edit_applicant", use_container_width=True):
                st.session_state.applicant_submitted = False
                st.session_state.result = None
                st.rerun()

    # ── RESULT PANEL ──────────────────────────────────────────────────────────
    with col_result:
        st.markdown("### 📊 Your Risk Assessment")

        result = st.session_state.result
        app    = st.session_state.applicant

        if result:
            rc    = RISK_COLOR[result["risk_level"]]
            rl    = result["risk_level"]

            st.markdown(f"""
            <div class="risk-badge" style="border-color:{rc}">
                <span class="risk-title" style="color:{rc}">{rl} Risk</span><br>
                <span>Default Probability: <b>{result['default_probability']*100:.2f}%</b></span><br>
                <span>Expected Loss: <b>₹{result['expected_loss']:,.2f}</b></span>
            </div>
            """, unsafe_allow_html=True)

            st.markdown(f"""
            <div class="recommendation" style="border-left-color:{rc}">
                <div class="rec-title">What this means for you:</div>
                <div class="rec-text">{APPLICANT_MSG[rl]}</div>
                <div class="rec-text" style="margin-top:6px;"><b>Suggested Action:</b> {result['recommended_action']}</div>
            </div>
            """, unsafe_allow_html=True)

            # Donut chart — default probability
            fig_donut = go.Figure(go.Pie(
                values=[result["default_probability"]*100, (1-result["default_probability"])*100],
                labels=["Default Risk %", "Safe %"],
                hole=0.62,
                marker_colors=[rc, "#1f2937"],
                textinfo="none",
                hoverinfo="label+percent",
            ))
            fig_donut.add_annotation(
                text=f"{result['default_probability']*100:.1f}%",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=22, color=rc)
            )
            fig_donut.update_layout(
                title="Probability of Default",
                paper_bgcolor="#111827", font=dict(color="white"),
                height=280, margin=dict(t=40, b=10, l=20, r=20),
                showlegend=True, legend=dict(orientation="h", y=-0.1)
            )
            st.plotly_chart(fig_donut, use_container_width=True, config={"displayModeBar": False})

            # Grouped bar — your value vs safe limit
            lir = result["loan_income_ratio"]
            lpr = result["loan_property_ratio"]
            fig_bar = go.Figure()
            fig_bar.add_trace(go.Bar(
                name="Your Value",
                y=["Loan / Income", "Loan / Property"],
                x=[lir, lpr],
                orientation="h",
                marker_color=[
                    "#22c55e" if lir <= SAFE_LIMITS["lir"] else "#ef4444",
                    "#22c55e" if lpr <= SAFE_LIMITS["lpr"] else "#ef4444",
                ],
                text=[round(lir,2), round(lpr,2)],
                textposition="outside",
            ))
            fig_bar.add_trace(go.Bar(
                name="Safe Limit",
                y=["Loan / Income", "Loan / Property"],
                x=[SAFE_LIMITS["lir"], SAFE_LIMITS["lpr"]],
                orientation="h",
                marker_color=["#374151", "#374151"],
                text=[f"Limit: {SAFE_LIMITS['lir']}", f"Limit: {SAFE_LIMITS['lpr']}"],
                textposition="outside",
            ))
            fig_bar.update_layout(
                barmode="group",
                paper_bgcolor="#111827", plot_bgcolor="#111827",
                font=dict(color="white"), height=230,
                margin=dict(t=10, b=30, l=120, r=70),
                xaxis=dict(gridcolor="#1f2937"),
                legend=dict(orientation="h", y=-0.25),
            )
            st.plotly_chart(fig_bar, use_container_width=True, config={"displayModeBar": False})
            st.markdown('<p style="font-size:12px;color:#9ca3af;">🟢 Green = within safe limit &nbsp;|&nbsp; 🔴 Red = exceeds limit &nbsp;|&nbsp; ⬛ Grey = safe benchmark</p>',
                        unsafe_allow_html=True)

        elif st.session_state.applicant_submitted:
            st.markdown('<p class="placeholder-text">✅ Your application has been submitted.<br><br>'
                        'Please wait while the bank staff reviews and assesses your application. '
                        'Once assessed, your result will appear here.</p>',
                        unsafe_allow_html=True)
        else:
            st.markdown('<p class="placeholder-text">Fill the form on the left and click '
                        '<b>Submit Application</b> to proceed.</p>',
                        unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# BANK PAGE
# ══════════════════════════════════════════════════════════════════════════════
def page_bank():
    render_header()
    st.markdown("<hr class='divider'>", unsafe_allow_html=True)
    st.markdown("### 🏦 Bank / Institution Dashboard")

    col_form, col_result = st.columns(2, gap="large")
    app     = st.session_state.applicant
    submitted = st.session_state.applicant_submitted

    # ── BANK FORM ─────────────────────────────────────────────────────────────
    with col_form:
        st.markdown("#### 📋 Submitted Application Summary")

        if submitted:
            ltv_display = app.get("ltv", 0.0)
            st.markdown(f"""
            <div style="background:#0f172a;border:1px solid #1f2937;border-radius:8px;padding:12px 16px;margin-bottom:1rem;">
            <table class="summary-table">
                <tr><td>Name</td><td>{app.get('name','—')}</td></tr>
                <tr><td>Age</td><td>{app.get('age','—')}</td></tr>
                <tr><td>Gender</td><td>{app.get('gender','—')}</td></tr>
                <tr><td>Annual Income</td><td>₹{int(app.get('income',0)):,}</td></tr>
                <tr><td>Employment</td><td>{app.get('occupation_type','—')}</td></tr>
                <tr><td>Loan Amount</td><td>₹{int(app.get('loan_amount',0)):,}</td></tr>
                <tr><td>Property Value</td><td>₹{int(app.get('property_value',0)):,}</td></tr>
                <tr><td>LTV</td><td>{ltv_display}%</td></tr>
                <tr><td>Loan Type</td><td>{app.get('loan_type','—')}</td></tr>
                <tr><td>Loan Purpose</td><td>{app.get('loan_purpose','—')}</td></tr>
                <tr><td>Region</td><td>{app.get('region','—')}</td></tr>
                <tr><td>Submission Mode</td><td>{app.get('submission_mode','—')}</td></tr>
            </table>
            </div>
            """, unsafe_allow_html=True)

            # Bank staff entry fields
            st.markdown('<p class="section-label bank-section-label">🏦 Bank Staff Entry</p>',
                        unsafe_allow_html=True)

            c1, c2 = st.columns(2)
            with c1:
                credit_score = st.number_input("Credit Score", min_value=300, max_value=900,
                                               value=700, step=1, key="credit_score",
                                               help="Fetched from CIBIL / Experian. Range: 500–900")
            with c2:
                dtir1 = st.number_input("Debt-to-Income Ratio %", min_value=0.0, max_value=100.0,
                                        value=30.0, step=0.5, key="dtir1",
                                        help="Monthly debt ÷ Monthly income × 100. Range: 5%–60%")

            c1, c2 = st.columns(2)
            with c1:
                rate_of_interest = st.number_input("Rate of Interest %", min_value=0.0,
                                                   max_value=30.0, value=9.5, step=0.1,
                                                   key="rate_of_interest",
                                                   help="Rate offered to this applicant. Range: 8.5%–11.5%")
            with c2:
                bank_interest_rate = st.number_input("Bank Base Rate %", min_value=0.0,
                                                     max_value=30.0, value=10.0, step=0.1,
                                                     key="bank_interest_rate",
                                                     help="Bank's internal benchmark rate")

            spread = round(bank_interest_rate - rate_of_interest, 2)
            st.markdown(f'<p style="font-size:13px;color:#9ca3af;margin-bottom:2px;">Interest Rate Spread <span style="color:#60a5fa;font-size:11px;">(auto-calculated)</span></p>'
                        f'<div class="readonly-field">{spread}%</div>', unsafe_allow_html=True)

            c1, c2 = st.columns(2)
            with c1:
                loan_limit = st.selectbox("Loan Limit",
                                          ["cf", "ncf"],
                                          format_func=lambda x: "Conforming (cf)" if x=="cf" else "Non-Conforming (ncf)",
                                          key="loan_limit")
            with c2:
                approv_in_adv = st.selectbox("Pre-Approved?",
                                             ["nopre", "pre"],
                                             format_func=lambda x: "No (nopre)" if x=="nopre" else "Yes (pre)",
                                             key="approv_in_adv")

            c1, c2 = st.columns(2)
            with c1:
                open_credit = st.selectbox("Open Credit Lines",
                                           ["nopc", "opc"],
                                           format_func=lambda x: "No Open Credit" if x=="nopc" else "Has Open Credit",
                                           key="open_credit")
            with c2:
                secured_by = st.selectbox("Secured By",
                                          ["home", "land"],
                                          format_func=lambda x: "Home" if x=="home" else "Land",
                                          key="secured_by")

            c1, c2 = st.columns(2)
            with c1:
                security_type = st.selectbox("Security Type",
                                             ["direct", "Indirect"],
                                             format_func=lambda x: "Direct" if x=="direct" else "Indirect",
                                             key="security_type")
            with c2:
                co_applicant_credit = st.selectbox("Co-Applicant Bureau",
                                                   ["EXP", "EQUI", "CRIF", "CIB"],
                                                   format_func=lambda x: {
                                                       "EXP":"EXP (Experian)",
                                                       "EQUI":"EQUI (Equifax)",
                                                       "CRIF":"CRIF",
                                                       "CIB":"CIB (CIBIL)"
                                                   }[x],
                                                   key="co_applicant_credit")

            submission_of = st.selectbox("Internal Routing",
                                         ["to_inst", "not_inst", "Branch", "Online"],
                                         format_func=lambda x: {
                                             "to_inst":"To Institution",
                                             "not_inst":"Not to Institution",
                                             "Branch":"Branch",
                                             "Online":"Online"
                                         }[x],
                                         key="submission_of")

            st.markdown("<br>", unsafe_allow_html=True)

            if st.button("🔍 Assess Risk", key="assess_risk", use_container_width=True):
                # Build encodings exactly as App.js handleBankAssess
                gender_enc      = 1 if app.get("gender") == "Male" else 0
                loan_limit_enc  = 2 if loan_limit == "cf" else 3
                approv_enc      = 2 if approv_in_adv == "nopre" else 3
                boc_enc         = 0 if app.get("biz_commercial") == "b/c" else 1
                occ_map         = {"ir": 0, "pr": 1, "sr": 2}
                occ_type_enc    = occ_map.get(app.get("occupancy_type", "pr"), 1)
                secured_enc     = 0 if secured_by == "home" else 1
                open_credit_enc = 1 if open_credit == "opc" else 0

                occ     = app.get("occupation_type", "Salaried")
                reg     = app.get("region", "central")
                lt      = app.get("loan_type", "Home Loan")
                lp      = app.get("loan_purpose", "House Purchase")
                sec_t   = security_type
                ass     = app.get("applicant_assurity", "Guarantor")
                sub_m   = app.get("submission_mode", "Online")

                payload = {
                    "ID": 0,
                    "age":                    int(app.get("age", 30)),
                    "Gender":                 gender_enc,
                    "income":                 float(app.get("income", 0)),
                    "year":                   2019,
                    "loan_limit":             loan_limit_enc,
                    "approv_in_adv":          approv_enc,
                    "business_or_commercial": boc_enc,
                    "loan_amount":            float(app.get("loan_amount", 0)),
                    "rate_of_interest":       float(rate_of_interest),
                    "bank_interest_rate":     float(bank_interest_rate),
                    "Interest_rate_spread":   float(spread),
                    "property_value":         float(app.get("property_value", 0)),
                    "occupancy_type":         occ_type_enc,
                    "Secured_by":             secured_enc,
                    "Credit_Score":           float(credit_score),
                    "open_credit":            open_credit_enc,
                    "LTV":                    float(app.get("ltv", 0)),
                    "dtir1":                  float(dtir1),
                    # occupation one-hot
                    "occupation_type_Professional":  1 if occ == "Professional"  else 0,
                    "occupation_type_Salaried":      1 if occ == "Salaried"      else 0,
                    "occupation_type_Self-Employed": 1 if occ == "Self-Employed" else 0,
                    # region one-hot
                    "Region_North-East": 1 if reg == "North-East" else 0,
                    "Region_central":    1 if reg == "central"    else 0,
                    "Region_south":      1 if reg == "south"      else 0,
                    # loan type one-hot
                    "loan_type_Education Loan": 1 if lt == "Education Loan" else 0,
                    "loan_type_Home Loan":      1 if lt == "Home Loan"      else 0,
                    "loan_type_Personal Loan":  1 if lt == "Personal Loan"  else 0,
                    # loan purpose one-hot
                    "loan_purpose_Debt Consolidation": 1 if lp == "Debt Consolidation" else 0,
                    "loan_purpose_Education":          1 if lp == "Education"           else 0,
                    "loan_purpose_House Purchase":     1 if lp == "House Purchase"      else 0,
                    "loan_purpose_Medical":            1 if lp == "Medical"             else 0,
                    # security
                    "Security_Type_direct":            1 if sec_t == "direct"     else 0,
                    "applicant_assurity_Guarantor":    1 if ass  == "Guarantor"   else 0,
                    "applicant_assurity_Property":     1 if ass  == "Property"    else 0,
                    # co-applicant credit
                    "co-applicant_credit_type_EXP":    1 if co_applicant_credit == "EXP" else 0,
                    # submission mode one-hot
                    "application_submission_mode_Branch Visit": 1 if sub_m == "Branch Visit" else 0,
                    "application_submission_mode_Online":       1 if sub_m == "Online"       else 0,
                    # submission of application one-hot
                    "submission_of_application_Branch":   1 if submission_of == "Branch"   else 0,
                    "submission_of_application_Online":   1 if submission_of == "Online"   else 0,
                    "submission_of_application_not_inst": 1 if submission_of == "not_inst" else 0,
                    "submission_of_application_to_inst":  1 if submission_of == "to_inst"  else 0,
                }

                with st.spinner("Running LightGBM inference..."):
                    result = run_inference(payload)

                st.session_state.result   = result
                st.session_state.bank_data = {
                    "credit_score": credit_score, "dtir1": dtir1,
                    "rate_of_interest": rate_of_interest,
                    "bank_interest_rate": bank_interest_rate,
                }
                st.rerun()

        else:
            st.markdown('<p class="placeholder-text">No application submitted yet.<br><br>'
                        'Go to the <b>Loan Applicant</b> page from the Home screen to submit an application first.</p>',
                        unsafe_allow_html=True)

    # ── RESULT PANEL ──────────────────────────────────────────────────────────
    with col_result:
        st.markdown("### 📊 Risk Assessment Result")

        result = st.session_state.result

        if result:
            rc = RISK_COLOR[result["risk_level"]]
            rl = result["risk_level"]

            # KPI cards
            st.markdown(f"""
            <div class="kpi-row">
                <div class="kpi-card">
                    <div class="kpi-label">Applicant</div>
                    <div class="kpi-value">{app.get('name','—')}</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-label">Risk Level</div>
                    <div class="kpi-value" style="color:{rc}">{rl}</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-label">Default Probability</div>
                    <div class="kpi-value">{result['default_probability']*100:.2f}%</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-label">Expected Loss</div>
                    <div class="kpi-value">₹{result['expected_loss']:,.0f}</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-label">Decision</div>
                    <div class="kpi-value" style="color:{rc};font-size:0.85rem">{result['bank_decision']}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown(f"""
            <div class="recommendation" style="border-left-color:{rc}">
                <div class="rec-title">Bank Recommendation:</div>
                <div class="rec-text">{BANK_MSG[rl]}</div>
            </div>
            """, unsafe_allow_html=True)

            # Gauge chart
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number",
                value=result["default_probability"] * 100,
                number={"suffix": "%", "font": {"size": 28, "color": rc}},
                gauge={
                    "axis": {"range": [0, 100], "tickcolor": "#9ca3af"},
                    "bar":  {"color": rc},
                    "bgcolor": "#1f2937", "bordercolor": "#374151",
                    "steps": [
                        {"range": [0,  25], "color": "#14532d"},
                        {"range": [25, 50], "color": "#713f12"},
                        {"range": [50, 75], "color": "#7f1d1d"},
                        {"range": [75,100], "color": "#450a0a"},
                    ],
                    "threshold": {"line": {"color": "white", "width": 3},
                                  "thickness": 0.75,
                                  "value": result["default_probability"] * 100},
                },
                title={"text": "Default Probability Gauge", "font": {"color": "white", "size": 14}},
            ))
            fig_gauge.update_layout(
                paper_bgcolor="#111827", font=dict(color="white"),
                height=300, margin=dict(t=40, b=20, l=30, r=30)
            )
            st.plotly_chart(fig_gauge, use_container_width=True, config={"displayModeBar": False})

            # Grouped bar — applicant vs benchmark
            lir = result["loan_income_ratio"]
            lpr = result["loan_property_ratio"]
            fig_bar = go.Figure()
            fig_bar.add_trace(go.Bar(
                name="Applicant Value",
                y=["Loan / Income", "Loan / Property"],
                x=[lir, lpr],
                orientation="h",
                marker_color=[
                    "#22c55e" if lir <= SAFE_LIMITS["lir"] else "#ef4444",
                    "#22c55e" if lpr <= SAFE_LIMITS["lpr"] else "#ef4444",
                ],
                text=[round(lir,2), round(lpr,2)],
                textposition="outside",
            ))
            fig_bar.add_trace(go.Bar(
                name="Safe Limit",
                y=["Loan / Income", "Loan / Property"],
                x=[SAFE_LIMITS["lir"], SAFE_LIMITS["lpr"]],
                orientation="h",
                marker_color=["#374151", "#374151"],
                text=[f"Limit: {SAFE_LIMITS['lir']}", f"Limit: {SAFE_LIMITS['lpr']}"],
                textposition="outside",
            ))
            fig_bar.update_layout(
                title="Applicant vs Safe Benchmark",
                barmode="group",
                paper_bgcolor="#111827", plot_bgcolor="#111827",
                font=dict(color="white"), height=260,
                margin=dict(t=40, b=20, l=120, r=70),
                xaxis=dict(gridcolor="#1f2937"),
                legend=dict(orientation="h", y=-0.2),
            )
            st.plotly_chart(fig_bar, use_container_width=True, config={"displayModeBar": False})

            # Feature engineering table
            st.markdown("#### 🔬 Engineered Feature Values")
            st.markdown(f"""
            <table class="fe-table">
                <thead>
                    <tr>
                        <th>Feature</th>
                        <th>Formula</th>
                        <th>Value</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>Loan / Income Ratio</td>
                        <td><span class="fe-formula">loan_amount / (income + 1)</span></td>
                        <td>{result['loan_income_ratio']}</td>
                    </tr>
                    <tr>
                        <td>Loan / Property Ratio</td>
                        <td><span class="fe-formula">loan_amount / (property_value + 1)</span></td>
                        <td>{result['loan_property_ratio']}</td>
                    </tr>
                    <tr>
                        <td>LTV × DTI Interaction</td>
                        <td><span class="fe-formula">LTV × dtir1</span></td>
                        <td>{result['LTV_dti_interaction']}</td>
                    </tr>
                    <tr>
                        <td>Credit / Income Ratio</td>
                        <td><span class="fe-formula">Credit_Score / (income + 1)</span></td>
                        <td>{result['credit_income_ratio']}</td>
                    </tr>
                </tbody>
            </table>
            """, unsafe_allow_html=True)

        elif submitted:
            st.markdown('<p class="placeholder-text">Fill in the bank details on the left and click '
                        '<b>Assess Risk</b> to see the result.</p>',
                        unsafe_allow_html=True)
        else:
            st.markdown('<p class="placeholder-text">Waiting for applicant to submit their application.</p>',
                        unsafe_allow_html=True)


# ── Router ────────────────────────────────────────────────────────────────────
if st.session_state.page == "home":
    page_home()
elif st.session_state.page == "user":
    page_user()
elif st.session_state.page == "bank":
    page_bank()