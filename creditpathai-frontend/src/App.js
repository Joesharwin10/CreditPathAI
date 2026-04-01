import React, { useState } from "react";
import axios from "axios";
import Plot from "react-plotly.js";
import "./App.css";

function Tip({ text }) {
  return (<span className="tip">?<span className="tip-box">{text}</span></span>);
}

function App() {
  const [page, setPage]     = useState("home");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  // Applicant fills this and clicks "Submit Application"
  // After that, applicantSubmitted = true and their data is locked/visible to bank
  const [applicantSubmitted, setApplicantSubmitted] = useState(false);

  const [applicant, setApplicant] = useState({
    name: "", age: "", gender: "Male", income: "",
    occupation_type: "Salaried", loan_amount: "", property_value: "",
    loan_type: "Home Loan", loan_purpose: "House Purchase",
    region: "central", occupancy_type: "pr",
    biz_commercial: "nob/c", applicant_assurity: "Guarantor",
    submission_mode: "Online",
  });

  // Bank fills this and clicks "Assess Risk"
  const [bank, setBank] = useState({
    credit_score: "", rate_of_interest: "", bank_interest_rate: "",
    dtir1: "", loan_limit: "cf", approv_in_adv: "nopre",
    open_credit: "nopc", secured_by: "home", security_type: "direct",
    co_applicant_credit: "EXP", submission_of: "to_inst",
  });

  const handleApplicant = (e) => setApplicant({ ...applicant, [e.target.name]: e.target.value });
  const handleBank      = (e) => setBank({ ...bank, [e.target.name]: e.target.value });

  // Auto-calculated from applicant inputs
  const loanAmt = Number(applicant.loan_amount)    || 0;
  const propVal = Number(applicant.property_value) || 0;
  const ltv     = propVal > 0 ? ((loanAmt / propVal) * 100).toFixed(2) : "0.00";

  // Auto-calculated from bank inputs
  const spread = bank.bank_interest_rate && bank.rate_of_interest
    ? (Number(bank.bank_interest_rate) - Number(bank.rate_of_interest)).toFixed(2) : "0.00";

  // ── Applicant clicks "Submit Application" ──────────────────
  const handleApplicantSubmit = () => {
    if (!applicant.name || !applicant.income || !applicant.loan_amount) {
      alert("Please fill in at least Name, Income, and Loan Amount.");
      return;
    }
    setApplicantSubmitted(true);
    setResult(null); // clear any previous result
  };

  // ── Bank clicks "Assess Risk" — this calls the API ─────────
  const handleBankAssess = async () => {
    if (!applicantSubmitted) {
      alert("No application submitted yet. Ask the applicant to fill and submit their form first.");
      return;
    }
    setLoading(true);
    try {
      // Label encoding — exactly from notebook cell 49
      const gender_enc      = applicant.gender === "Male" ? 1 : 0;
      const loan_limit_enc  = bank.loan_limit === "cf" ? 2 : 3;
      const approv_enc      = bank.approv_in_adv === "nopre" ? 2 : 3;
      const boc_enc         = applicant.biz_commercial === "b/c" ? 0 : 1;
      const occ_type_enc    = { ir: 0, pr: 1, sr: 2 }[applicant.occupancy_type] ?? 1;
      const secured_enc     = bank.secured_by === "home" ? 0 : 1;
      const open_credit_enc = bank.open_credit === "opc" ? 1 : 0;

      const payload = {
        data: {
          ID: 0,
          age:                    Number(applicant.age),
          Gender:                 gender_enc,
          income:                 Number(applicant.income),
          year:                   2019,
          loan_limit:             loan_limit_enc,
          approv_in_adv:          approv_enc,
          business_or_commercial: boc_enc,
          loan_amount:            loanAmt,
          rate_of_interest:       Number(bank.rate_of_interest),
          bank_interest_rate:     Number(bank.bank_interest_rate),
          Interest_rate_spread:   Number(spread),
          property_value:         propVal,
          occupancy_type:         occ_type_enc,
          Secured_by:             secured_enc,
          Credit_Score:           Number(bank.credit_score),
          open_credit:            open_credit_enc,
          LTV:                    Number(ltv),
          dtir1:                  Number(bank.dtir1),
          "occupation_type_Professional":  applicant.occupation_type === "Professional"  ? 1 : 0,
          "occupation_type_Salaried":      applicant.occupation_type === "Salaried"      ? 1 : 0,
          "occupation_type_Self-Employed": applicant.occupation_type === "Self-Employed" ? 1 : 0,
          "Region_North-East": applicant.region === "North-East" ? 1 : 0,
          "Region_central":    applicant.region === "central"    ? 1 : 0,
          "Region_south":      applicant.region === "south"      ? 1 : 0,
          "loan_type_Education Loan": applicant.loan_type === "Education Loan" ? 1 : 0,
          "loan_type_Home Loan":      applicant.loan_type === "Home Loan"      ? 1 : 0,
          "loan_type_Personal Loan":  applicant.loan_type === "Personal Loan"  ? 1 : 0,
          "loan_purpose_Debt Consolidation": applicant.loan_purpose === "Debt Consolidation" ? 1 : 0,
          "loan_purpose_Education":          applicant.loan_purpose === "Education"           ? 1 : 0,
          "loan_purpose_House Purchase":     applicant.loan_purpose === "House Purchase"      ? 1 : 0,
          "loan_purpose_Medical":            applicant.loan_purpose === "Medical"             ? 1 : 0,
          "Security_Type_direct":            bank.security_type === "direct"            ? 1 : 0,
          "applicant_assurity_Guarantor":    applicant.applicant_assurity === "Guarantor" ? 1 : 0,
          "applicant_assurity_Property":     applicant.applicant_assurity === "Property"  ? 1 : 0,
          "co-applicant_credit_type_EXP":    bank.co_applicant_credit === "EXP"         ? 1 : 0,
          "application_submission_mode_Branch Visit": applicant.submission_mode === "Branch Visit" ? 1 : 0,
          "application_submission_mode_Online":       applicant.submission_mode === "Online"       ? 1 : 0,
          "submission_of_application_Branch":   bank.submission_of === "Branch"   ? 1 : 0,
          "submission_of_application_Online":   bank.submission_of === "Online"   ? 1 : 0,
          "submission_of_application_not_inst": bank.submission_of === "not_inst" ? 1 : 0,
          "submission_of_application_to_inst":  bank.submission_of === "to_inst"  ? 1 : 0,
        }
      };

      const res = await axios.post("http://127.0.0.1:8000/risk-score", payload);
      setResult(res.data);
    } catch (err) {
      console.error(err);
      alert("API error — make sure FastAPI is running:\nuvicorn api:app --reload");
    }
    setLoading(false);
  };

  // ── Helpers ───────────────────────────────────────────────
  const riskColor = { Low: "#22c55e", Medium: "#f59e0b", High: "#ef4444", Critical: "#dc2626" };

  const applicantMsg = {
    Low:      "Your financial profile looks healthy. You are likely to get loan approval.",
    Medium:   "Your profile has some risk. Consider reducing the loan amount or improving repayment history.",
    High:     "High financial risk detected. Apply for a smaller loan or increase your down payment.",
    Critical: "Critical risk level. Please consult a financial advisor before proceeding.",
  };

  const bankMsg = {
    Low:      "Low risk borrower. Safe to approve the loan under standard terms.",
    Medium:   "Moderate risk. Approve with conditions — higher down payment or co-applicant required.",
    High:     "High risk borrower. Assign a recovery officer and request additional collateral.",
    Critical: "Critical risk. Legal review required before any approval decision.",
  };

  const T = { lir: 3.0, lpr: 4.0 };

  // ══════════════════════════════════════════════════════════
  // HOME PAGE
  // ══════════════════════════════════════════════════════════
  if (page === "home") return (
    <div className="container">
      <h1>💳 CreditPathAI</h1>
      <p className="subtitle">AI-Powered Loan Risk Intelligence System</p>
      <p className="home-desc">Welcome! Please select who you are to get started.</p>
      <div className="home-grid">
        <div className="home-card" onClick={() => setPage("user")}>
          <div className="home-icon">👤</div>
          <h2>Loan Applicant</h2>
          <p>I am applying for a loan. I want to fill my application details and see my risk assessment result.</p>
          <div className="home-btn">Start Application →</div>
        </div>
        <div className="home-card" onClick={() => setPage("bank")}>
          <div className="home-icon">🏦</div>
          <h2>Bank / Institution</h2>
          <p>I am a bank staff member. I will review the submitted application, enter bank details, and assess the risk.</p>
          <div className="home-btn">Open Dashboard →</div>
        </div>
      </div>
    </div>
  );

  // ══════════════════════════════════════════════════════════
  // APPLICANT PAGE
  // Applicant fills personal + loan details and submits.
  // After submission, they see their result (once bank assesses).
  // ══════════════════════════════════════════════════════════
  if (page === "user") return (
    <div className="container">
      <div className="page-header">
        <div>
          <h1>💳 CreditPathAI</h1>
          <p className="subtitle">AI-Powered Loan Risk Intelligence System</p>
        </div>
        <button className="back-btn" onClick={() => setPage("home")}>← Back to Home</button>
      </div>

      <div className="grid">

        {/* ── APPLICANT FORM ── */}
        <div className="card">
          <h2>👤 Loan Application Form</h2>

          {applicantSubmitted && (
            <div className="submitted-banner">
              ✅ Application submitted! The bank staff will now review and assess your risk.
            </div>
          )}

          <p className="section-label">Personal Details</p>

          <label>Full Name <Tip text="Enter your full legal name as per your ID proof." /></label>
          <input name="name" placeholder="e.g. Arjun Sharma"
            defaultValue={applicant.name} onChange={handleApplicant}
            disabled={applicantSubmitted} />

          <div className="row2">
            <div>
              <label>Age <Tip text="Must be 21 or above." /></label>
              <input name="age" type="number" placeholder="e.g. 35"
                defaultValue={applicant.age} onChange={handleApplicant}
                disabled={applicantSubmitted} />
            </div>
            <div>
              <label>Gender <Tip text="As per official documents." /></label>
              <select name="gender" onChange={handleApplicant} disabled={applicantSubmitted}>
                <option>Male</option><option>Female</option>
              </select>
            </div>
          </div>

          <label>Annual Income (₹) <Tip text="Total yearly income before tax. Range: ₹2L–₹20L." /></label>
          <input name="income" type="number" placeholder="e.g. 1000000"
            defaultValue={applicant.income} onChange={handleApplicant}
            disabled={applicantSubmitted} />

          <label>Employment Type <Tip text="Salaried = employed. Professional = doctor/lawyer/CA. Self-Employed = own business. Business/Other = business owner." /></label>
          <select name="occupation_type" onChange={handleApplicant} disabled={applicantSubmitted}>
            <option value="Salaried">Salaried</option>
            <option value="Professional">Professional (Doctor / Lawyer / CA)</option>
            <option value="Self-Employed">Self-Employed</option>
            <option value="Business">Business / Other</option>
          </select>

          <p className="section-label">Loan Details</p>

          <div className="row2">
            <div>
              <label>Loan Amount (₹) <Tip text="Amount you want to borrow." /></label>
              <input name="loan_amount" type="number" placeholder="e.g. 2000000"
                defaultValue={applicant.loan_amount} onChange={handleApplicant}
                disabled={applicantSubmitted} />
            </div>
            <div>
              <label>Property Value (₹) <Tip text="Current market value of the property." /></label>
              <input name="property_value" type="number" placeholder="e.g. 3000000"
                defaultValue={applicant.property_value} onChange={handleApplicant}
                disabled={applicantSubmitted} />
            </div>
          </div>

          <label>LTV — Loan to Value Ratio <Tip text="Auto-calculated: Loan ÷ Property × 100. Typical dataset range: 60%–95%." /></label>
          <input value={`${ltv}%  (auto-calculated)`} readOnly className="readonly" />

          <div className="row2">
            <div>
              <label>Loan Type <Tip text="Home = property. Education = studies. Personal = general. Business = business/debt consolidation." /></label>
              <select name="loan_type" onChange={handleApplicant} disabled={applicantSubmitted}>
                <option value="Home Loan">Home Loan</option>
                <option value="Education Loan">Education Loan</option>
                <option value="Personal Loan">Personal Loan</option>
                <option value="Business Loan">Business Loan / Debt Consolidation</option>
              </select>
            </div>
            <div>
              <label>Loan Purpose <Tip text="What will you use this loan for?" /></label>
              <select name="loan_purpose" onChange={handleApplicant} disabled={applicantSubmitted}>
                <option value="House Purchase">House Purchase</option>
                <option value="Education">Education</option>
                <option value="Medical">Medical</option>
                <option value="Debt Consolidation">Debt Consolidation</option>
              </select>
            </div>
          </div>

          <p className="section-label">Property & Other Details</p>

          <div className="row2">
            <div>
              <label>Region <Tip text="Region where the property is located." /></label>
              <select name="region" onChange={handleApplicant} disabled={applicantSubmitted}>
                <option value="central">Central</option>
                <option value="North-East">North-East</option>
                <option value="south">South</option>
              </select>
            </div>
            <div>
              <label>Occupancy Type <Tip text="pr = Primary Residence. sr = Secondary home. ir = Investment/Rental." /></label>
              <select name="occupancy_type" onChange={handleApplicant} disabled={applicantSubmitted}>
                <option value="pr">Primary Residence (pr)</option>
                <option value="sr">Secondary Residence (sr)</option>
                <option value="ir">Investment / Rental (ir)</option>
              </select>
            </div>
          </div>

          <div className="row2">
            <div>
              <label>Business / Commercial? <Tip text="Is this loan for business use?" /></label>
              <select name="biz_commercial" onChange={handleApplicant} disabled={applicantSubmitted}>
                <option value="nob/c">No — Personal Use</option>
                <option value="b/c">Yes — Business Use</option>
              </select>
            </div>
            <div>
              <label>Applicant Assurity <Tip text="Guarantor = someone vouches. Property = property pledged." /></label>
              <select name="applicant_assurity" onChange={handleApplicant} disabled={applicantSubmitted}>
                <option value="Guarantor">Guarantor</option>
                <option value="Property">Property</option>
              </select>
            </div>
          </div>

          <label>Submission Mode <Tip text="Online = bank website. Branch Visit = in person." /></label>
          <select name="submission_mode" onChange={handleApplicant} disabled={applicantSubmitted}>
            <option value="Online">Online</option>
            <option value="Branch Visit">Branch Visit</option>
          </select>

          {!applicantSubmitted ? (
            <button onClick={handleApplicantSubmit}>Submit Application</button>
          ) : (
            <button className="secondary-btn" onClick={() => { setApplicantSubmitted(false); setResult(null); }}>
              Edit Application
            </button>
          )}
        </div>

        {/* ── APPLICANT RESULT ── */}
        <div className="card">
          <h2>📊 Your Risk Assessment</h2>

          {result ? (
            <>
              <p><b>Applicant:</b> {applicant.name || "—"}</p>

              <div className="risk-badge" style={{ borderColor: riskColor[result.risk_level] }}>
                <span style={{ color: riskColor[result.risk_level], fontSize: "1.5em", fontWeight: "bold" }}>
                  {result.risk_level} Risk
                </span><br />
                <span>Default Probability: {(result.default_probability * 100).toFixed(2)}%</span><br />
                <span>Expected Loss: ₹{result.expected_loss.toLocaleString()}</span>
              </div>

              <div className="recommendation"
                style={{ borderLeft: `4px solid ${riskColor[result.risk_level]}` }}>
                <b>What this means for you:</b>
                <p>{applicantMsg[result.risk_level]}</p>
                <p><b>Suggested Action:</b> {result.recommended_action}</p>
              </div>

              {/* Default probability donut */}
              <h3>Your Default Risk</h3>
              <Plot
                data={[{
                  values: [result.default_probability * 100, (1 - result.default_probability) * 100],
                  labels: ["Default Risk %", "Safe %"],
                  type: "pie", hole: 0.6,
                  marker: { colors: [riskColor[result.risk_level], "#1f2937"] },
                  textinfo: "none",
                  hoverinfo: "label+percent",
                }]}
                layout={{
                  annotations: [{
                    text: `${(result.default_probability * 100).toFixed(1)}%`,
                    x: 0.5, y: 0.5,
                    font: { size: 22, color: riskColor[result.risk_level] },
                    showarrow: false
                  }],
                  title: "Probability of Default",
                  paper_bgcolor: "#111827", font: { color: "white" },
                  height: 280, margin: { t: 40, b: 10, l: 20, r: 20 },
                  showlegend: true, legend: { orientation: "h", y: -0.1 }
                }}
                style={{ width: "100%" }} config={{ displayModeBar: false }}
              />

              {/* Your value vs safe limit */}
              <h3>Your Value vs Safe Limit</h3>
              <Plot
                data={[
                  {
                    name: "Your Value",
                    y: ["Loan / Income", "Loan / Property"],
                    x: [result.loan_income_ratio, result.loan_property_ratio],
                    type: "bar", orientation: "h",
                    marker: {
                      color: [
                        result.loan_income_ratio   <= T.lir ? "#22c55e" : "#ef4444",
                        result.loan_property_ratio <= T.lpr ? "#22c55e" : "#ef4444",
                      ]
                    },
                    text: [result.loan_income_ratio, result.loan_property_ratio],
                    textposition: "outside",
                  },
                  {
                    name: "Safe Limit",
                    y: ["Loan / Income", "Loan / Property"],
                    x: [T.lir, T.lpr],
                    type: "bar", orientation: "h",
                    marker: { color: ["#374151", "#374151"] },
                    text: [`Limit: ${T.lir}`, `Limit: ${T.lpr}`],
                    textposition: "outside",
                  }
                ]}
                layout={{
                  barmode: "group",
                  paper_bgcolor: "#111827", plot_bgcolor: "#111827",
                  font: { color: "white" }, height: 230,
                  margin: { t: 10, b: 30, l: 120, r: 70 },
                  xaxis: { gridcolor: "#1f2937" },
                  legend: { orientation: "h", y: -0.25 }
                }}
                style={{ width: "100%" }} config={{ displayModeBar: false }}
              />
              <p className="fe-note">🟢 Green = within safe limit &nbsp;|&nbsp; 🔴 Red = exceeds limit &nbsp;|&nbsp; ⬛ Grey = safe benchmark</p>
            </>
          ) : applicantSubmitted ? (
            <p className="placeholder">
              ✅ Your application has been submitted.<br /><br />
              Please wait while the bank staff reviews and assesses your application.
              Once assessed, your result will appear here.
            </p>
          ) : (
            <p className="placeholder">
              Fill the form on the left and click <b>Submit Application</b> to proceed.
            </p>
          )}
        </div>
      </div>
    </div>
  );

  // ══════════════════════════════════════════════════════════
  // BANK PAGE
  // Bank sees applicant's submitted data, fills their own
  // fields, clicks "Assess Risk" to get the prediction.
  // ══════════════════════════════════════════════════════════
  if (page === "bank") return (
    <div className="container">
      <div className="page-header">
        <div>
          <h1>💳 CreditPathAI</h1>
          <p className="subtitle">AI-Powered Loan Risk Intelligence System</p>
        </div>
        <button className="back-btn" onClick={() => setPage("home")}>← Back to Home</button>
      </div>

      <h2>🏦 Bank / Institution Dashboard</h2>

      <div className="grid">

        {/* ── BANK FORM ── */}
        <div className="card">

          {/* Applicant summary — read only, shown to bank staff */}
          <h3>📋 Submitted Application Summary</h3>
          {applicantSubmitted ? (
            <div className="applicant-summary">
              <div className="summary-row"><span>Name</span><span>{applicant.name || "—"}</span></div>
              <div className="summary-row"><span>Age</span><span>{applicant.age || "—"}</span></div>
              <div className="summary-row"><span>Gender</span><span>{applicant.gender}</span></div>
              <div className="summary-row"><span>Annual Income</span><span>₹{Number(applicant.income).toLocaleString() || "—"}</span></div>
              <div className="summary-row"><span>Employment</span><span>{applicant.occupation_type}</span></div>
              <div className="summary-row"><span>Loan Amount</span><span>₹{Number(applicant.loan_amount).toLocaleString() || "—"}</span></div>
              <div className="summary-row"><span>Property Value</span><span>₹{Number(applicant.property_value).toLocaleString() || "—"}</span></div>
              <div className="summary-row"><span>LTV</span><span>{ltv}%</span></div>
              <div className="summary-row"><span>Loan Type</span><span>{applicant.loan_type}</span></div>
              <div className="summary-row"><span>Loan Purpose</span><span>{applicant.loan_purpose}</span></div>
              <div className="summary-row"><span>Region</span><span>{applicant.region}</span></div>
              <div className="summary-row"><span>Submission Mode</span><span>{applicant.submission_mode}</span></div>
            </div>
          ) : (
            <p className="placeholder">
              No application submitted yet.&nbsp;
              <span className="link" onClick={() => setPage("user")}>Go to Loan Applicant</span>
              &nbsp;to submit an application first.
            </p>
          )}

          {/* Bank staff entry — only shown after applicant submits */}
          {applicantSubmitted && (
            <>
              <p className="section-label bank-section-label">
                🏦 Bank Staff Entry
                <span className="staff-note"> — Enter your assessment details below</span>
              </p>

              <div className="row2">
                <div>
                  <label>Credit Score <Tip text="Fetched from CIBIL / Experian. Range: 500–900." /></label>
                  <input name="credit_score" type="number" placeholder="500–900" onChange={handleBank} />
                </div>
                <div>
                  <label>Debt-to-Income Ratio % <Tip text="Monthly debt ÷ Monthly income × 100. Range: 5%–60%." /></label>
                  <input name="dtir1" type="number" placeholder="5–60" onChange={handleBank} />
                </div>
              </div>

              <div className="row2">
                <div>
                  <label>Rate of Interest % <Tip text="Rate offered to this applicant. Range: 8.5%–11.5%." /></label>
                  <input name="rate_of_interest" type="number" placeholder="8.5–11.5" onChange={handleBank} />
                </div>
                <div>
                  <label>Bank Base Rate % <Tip text="Bank's internal benchmark rate. Range: 8.5%–11.5%." /></label>
                  <input name="bank_interest_rate" type="number" placeholder="8.5–11.5" onChange={handleBank} />
                </div>
              </div>

              <label>Interest Rate Spread <Tip text="Auto-calculated: Bank Base Rate − Applicant Rate." /></label>
              <input value={`${spread}%  (auto-calculated)`} readOnly className="readonly" />

              <div className="row2">
                <div>
                  <label>Loan Limit <Tip text="cf = Conforming. ncf = Non-Conforming (exceeds standard limits)." /></label>
                  <select name="loan_limit" onChange={handleBank}>
                    <option value="cf">Conforming (cf)</option>
                    <option value="ncf">Non-Conforming (ncf)</option>
                  </select>
                </div>
                <div>
                  <label>Pre-Approved? <Tip text="nopre = Not pre-approved. pre = Pre-approved." /></label>
                  <select name="approv_in_adv" onChange={handleBank}>
                    <option value="nopre">No (nopre)</option>
                    <option value="pre">Yes (pre)</option>
                  </select>
                </div>
              </div>

              <div className="row2">
                <div>
                  <label>Open Credit Lines <Tip text="nopc = No open credit. opc = Has open credit." /></label>
                  <select name="open_credit" onChange={handleBank}>
                    <option value="nopc">No Open Credit</option>
                    <option value="opc">Has Open Credit</option>
                  </select>
                </div>
                <div>
                  <label>Secured By <Tip text="Collateral backing the loan." /></label>
                  <select name="secured_by" onChange={handleBank}>
                    <option value="home">Home</option>
                    <option value="land">Land</option>
                  </select>
                </div>
              </div>

              <div className="row2">
                <div>
                  <label>Security Type <Tip text="Direct = applicant provides directly. Indirect = via third party." /></label>
                  <select name="security_type" onChange={handleBank}>
                    <option value="direct">Direct</option>
                    <option value="Indirect">Indirect</option>
                  </select>
                </div>
                <div>
                  <label>Co-Applicant Bureau <Tip text="EXP=Experian, EQUI=Equifax, CRIF=CRIF, CIB=CIBIL." /></label>
                  <select name="co_applicant_credit" onChange={handleBank}>
                    <option value="EXP">EXP (Experian)</option>
                    <option value="EQUI">EQUI (Equifax)</option>
                    <option value="CRIF">CRIF</option>
                    <option value="CIB">CIB (CIBIL)</option>
                  </select>
                </div>
              </div>

              <label>Internal Routing <Tip text="How this application is routed internally." /></label>
              <select name="submission_of" onChange={handleBank}>
                <option value="to_inst">To Institution</option>
                <option value="not_inst">Not to Institution</option>
                <option value="Branch">Branch</option>
                <option value="Online">Online</option>
              </select>

              <button onClick={handleBankAssess} disabled={loading}>
                {loading ? "Assessing..." : "Assess Risk"}
              </button>
            </>
          )}
        </div>

        {/* ── BANK RESULT ── */}
        <div className="card">
          <h2>📊 Risk Assessment Result</h2>

          {result ? (
            <>
              <div className="bank-summary">
                {[
                  ["Applicant",           applicant.name || "—"],
                  ["Risk Level",          result.risk_level,                              riskColor[result.risk_level]],
                  ["Default Probability", (result.default_probability * 100).toFixed(2) + "%"],
                  ["Expected Loss",       "₹" + result.expected_loss.toLocaleString()],
                  ["Decision",            result.bank_decision,                           riskColor[result.risk_level]],
                ].map(([label, val, color]) => (
                  <div className="bank-kpi" key={label}>
                    <span className="kpi-label">{label}</span>
                    <span className="kpi-value" style={color ? { color } : {}}>{val}</span>
                  </div>
                ))}
              </div>

              <div className="recommendation"
                style={{ borderLeft: `4px solid ${riskColor[result.risk_level]}` }}>
                <b>Bank Recommendation:</b>
                <p>{bankMsg[result.risk_level]}</p>
              </div>

              {/* Gauge chart */}
              <Plot
                data={[{
                  type: "indicator",
                  mode: "gauge+number",
                  value: result.default_probability * 100,
                  number: { suffix: "%", font: { size: 28, color: riskColor[result.risk_level] } },
                  gauge: {
                    axis: { range: [0, 100], tickcolor: "#9ca3af" },
                    bar: { color: riskColor[result.risk_level] },
                    bgcolor: "#1f2937", bordercolor: "#374151",
                    steps: [
                      { range: [0,  25], color: "#14532d" },
                      { range: [25, 50], color: "#713f12" },
                      { range: [50, 75], color: "#7f1d1d" },
                      { range: [75,100], color: "#450a0a" },
                    ],
                    threshold: { line: { color: "white", width: 3 }, thickness: 0.75, value: result.default_probability * 100 }
                  },
                  title: { text: "Default Probability Gauge", font: { color: "white", size: 14 } }
                }]}
                layout={{
                  paper_bgcolor: "#111827", font: { color: "white" },
                  height: 300, margin: { t: 40, b: 20, l: 30, r: 30 }
                }}
                style={{ width: "100%" }} config={{ displayModeBar: false }}
              />

              {/* Applicant vs benchmark grouped bar */}
              <Plot
                data={[
                  {
                    name: "Applicant Value",
                    y: ["Loan / Income", "Loan / Property"],
                    x: [result.loan_income_ratio, result.loan_property_ratio],
                    type: "bar", orientation: "h",
                    marker: {
                      color: [
                        result.loan_income_ratio   <= T.lir ? "#22c55e" : "#ef4444",
                        result.loan_property_ratio <= T.lpr ? "#22c55e" : "#ef4444",
                      ]
                    },
                    text: [result.loan_income_ratio, result.loan_property_ratio],
                    textposition: "outside",
                  },
                  {
                    name: "Safe Limit",
                    y: ["Loan / Income", "Loan / Property"],
                    x: [T.lir, T.lpr],
                    type: "bar", orientation: "h",
                    marker: { color: ["#374151", "#374151"] },
                    text: [`Limit: ${T.lir}`, `Limit: ${T.lpr}`],
                    textposition: "outside",
                  }
                ]}
                layout={{
                  title: "Applicant vs Safe Benchmark",
                  barmode: "group",
                  paper_bgcolor: "#111827", plot_bgcolor: "#111827",
                  font: { color: "white" }, height: 260,
                  margin: { t: 40, b: 20, l: 120, r: 70 },
                  xaxis: { gridcolor: "#1f2937" },
                  legend: { orientation: "h", y: -0.2 }
                }}
                style={{ width: "100%" }} config={{ displayModeBar: false }}
              />
            </>
          ) : applicantSubmitted ? (
            <p className="placeholder">
              Fill in the bank details on the left and click <b>Assess Risk</b> to see the result.
            </p>
          ) : (
            <p className="placeholder">
              Waiting for applicant to submit their application.
            </p>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;