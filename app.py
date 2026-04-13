import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import date

st.set_page_config(page_title="Farm Monthly Report", layout="wide")

# -----------------------------
# Helpers
# -----------------------------
def init_session_state():
    defaults = {
        "work_rows": [
            {"date": "", "task": "", "materials": "", "hours_or_people": ""}
        ],
        "expense_rows": [
            {"date": "", "item": "", "amount": 0.0, "purpose": "", "receipt": "Yes"}
        ],
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def to_excel_bytes(summary_df: pd.DataFrame, work_df: pd.DataFrame, expense_df: pd.DataFrame) -> bytes:
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        summary_df.to_excel(writer, index=False, sheet_name="Summary")
        work_df.to_excel(writer, index=False, sheet_name="Work Log")
        expense_df.to_excel(writer, index=False, sheet_name="Expenses")
    return output.getvalue()


def calc_report_score(on_time: bool, consistency: str, clarity: str, receipt_rate: float) -> tuple[float, float]:
    score = 0

    # 1) Timeliness: 20
    score += 20 if on_time else 10

    # 2) Consistency / completeness: 30
    consistency_map = {
        "Very good": 30,
        "Good": 24,
        "Average": 18,
        "Needs improvement": 10,
    }
    score += consistency_map.get(consistency, 18)

    # 3) Clarity: 20
    clarity_map = {
        "Very clear": 20,
        "Clear": 16,
        "Average": 12,
        "Unclear": 6,
    }
    score += clarity_map.get(clarity, 12)

    # 4) Receipt coverage: 30
    if receipt_rate >= 1.0:
        score += 30
    elif receipt_rate >= 0.9:
        score += 26
    elif receipt_rate >= 0.75:
        score += 20
    elif receipt_rate >= 0.5:
        score += 12
    else:
        score += 5

    # Multiplier conversion
    if score >= 90:
        multiplier = 1.10
    elif score >= 80:
        multiplier = 1.05
    elif score >= 70:
        multiplier = 1.00
    elif score >= 60:
        multiplier = 0.95
    else:
        multiplier = 0.90

    return float(score), float(multiplier)


# -----------------------------
# App
# -----------------------------
init_session_state()

st.title("🌱 Monthly Farm Report & Evaluation")
st.caption("Monthly report input + basic evaluation score (prototype)")

with st.sidebar:
    st.header("Evaluation Policy")
    st.markdown(
        """
        **Current prototype formula**  
        Evaluation Score = (Harvest / Area) × Land Difficulty Coefficient × Report Multiplier

        - Harvest / Area = yield per ha
        - Land Difficulty Coefficient = higher for harder land
        - Report Multiplier = based on report quality and receipt coverage
        """
    )

# -----------------------------
# 1. Basic info
# -----------------------------
st.subheader("1. Basic Information")
col1, col2, col3, col4 = st.columns(4)
with col1:
    employee_name = st.text_input("Employee Name")
with col2:
    plot_id = st.text_input("Plot ID")
with col3:
    report_month = st.text_input("Target Month", value=f"{date.today().year}-{date.today().month:02d}")
with col4:
    office = st.text_input("Office / Area")

col1, col2, col3 = st.columns(3)
with col1:
    area_ha = st.number_input("Managed Area (ha)", min_value=0.01, value=1.00, step=0.01)
with col2:
    harvest_kg = st.number_input("Monthly Harvest (kg)", min_value=0.0, value=0.0, step=1.0)
with col3:
    cumulative_harvest_kg = st.number_input("Cumulative Harvest (kg)", min_value=0.0, value=0.0, step=1.0)

col1, col2 = st.columns(2)
with col1:
    land_difficulty = st.selectbox(
        "Land Difficulty",
        options=[
            "Standard (1.00)",
            "Slightly Difficult (1.10)",
            "Difficult (1.20)",
            "Very Difficult (1.30)",
        ],
    )
with col2:
    weather_notes = st.text_area("Weather / Land Condition Notes", height=100)

land_coeff_map = {
    "Standard (1.00)": 1.00,
    "Slightly Difficult (1.10)": 1.10,
    "Difficult (1.20)": 1.20,
    "Very Difficult (1.30)": 1.30,
}
land_coeff = land_coeff_map[land_difficulty]

# -----------------------------
# 2. Work logs
# -----------------------------
st.subheader("2. Work Log")
col_a, col_b = st.columns([1, 4])
with col_a:
    if st.button("+ Add Work Row"):
        st.session_state.work_rows.append(
            {"date": "", "task": "", "materials": "", "hours_or_people": ""}
        )
with col_b:
    st.caption("Examples: fertilizing, weeding, harvesting, irrigation, pest control")

updated_work_rows = []
for i, row in enumerate(st.session_state.work_rows):
    c1, c2, c3, c4 = st.columns([1.2, 2.5, 2.0, 1.5])
    with c1:
        row_date = st.text_input(f"Date #{i+1}", value=row["date"], key=f"work_date_{i}")
    with c2:
        task = st.text_input(f"Task #{i+1}", value=row["task"], key=f"work_task_{i}")
    with c3:
        materials = st.text_input(f"Materials #{i+1}", value=row["materials"], key=f"work_materials_{i}")
    with c4:
        hours_or_people = st.text_input(
            f"Hours/People #{i+1}", value=row["hours_or_people"], key=f"work_hours_{i}"
        )
    updated_work_rows.append(
        {
            "date": row_date,
            "task": task,
            "materials": materials,
            "hours_or_people": hours_or_people,
        }
    )
st.session_state.work_rows = updated_work_rows

# -----------------------------
# 3. Expense logs
# -----------------------------
st.subheader("3. Expense Report")
col_a, col_b = st.columns([1, 4])
with col_a:
    if st.button("+ Add Expense Row"):
        st.session_state.expense_rows.append(
            {"date": "", "item": "", "amount": 0.0, "purpose": "", "receipt": "Yes"}
        )
with col_b:
    st.caption("Examples: fertilizer, tools, transportation, irrigation supplies")

updated_expense_rows = []
for i, row in enumerate(st.session_state.expense_rows):
    c1, c2, c3, c4, c5 = st.columns([1.2, 2.0, 1.2, 2.4, 1.0])
    with c1:
        row_date = st.text_input(f"Expense Date #{i+1}", value=row["date"], key=f"exp_date_{i}")
    with c2:
        item = st.text_input(f"Item #{i+1}", value=row["item"], key=f"exp_item_{i}")
    with c3:
        amount = st.number_input(f"Amount #{i+1}", min_value=0.0, value=float(row["amount"]), step=1.0, key=f"exp_amount_{i}")
    with c4:
        purpose = st.text_input(f"Purpose #{i+1}", value=row["purpose"], key=f"exp_purpose_{i}")
    with c5:
        receipt = st.selectbox(f"Receipt #{i+1}", ["Yes", "No"], index=0 if row["receipt"] == "Yes" else 1, key=f"exp_receipt_{i}")
    updated_expense_rows.append(
        {
            "date": row_date,
            "item": item,
            "amount": amount,
            "purpose": purpose,
            "receipt": receipt,
        }
    )
st.session_state.expense_rows = updated_expense_rows

# -----------------------------
# 4. Issues / next month plan
# -----------------------------
st.subheader("4. Issues / Next Month Plan")
issues = st.text_area("Issues / Problems", height=120)
actions = st.text_area("Actions Taken / Planned Next Month", height=120)

# -----------------------------
# 5. Report quality inputs
# -----------------------------
st.subheader("5. Report Quality Review")
st.caption("For now, this can be filled by the manager or admin.")

col1, col2, col3 = st.columns(3)
with col1:
    on_time = st.checkbox("Submitted on time", value=True)
with col2:
    consistency = st.selectbox("Completeness / Consistency", ["Very good", "Good", "Average", "Needs improvement"])
with col3:
    clarity = st.selectbox("Clarity", ["Very clear", "Clear", "Average", "Unclear"])

# -----------------------------
# Calculation
# -----------------------------
work_df = pd.DataFrame(st.session_state.work_rows)
expense_df = pd.DataFrame(st.session_state.expense_rows)

valid_expense_df = expense_df[
    (expense_df["item"].astype(str).str.strip() != "") |
    (expense_df["purpose"].astype(str).str.strip() != "") |
    (expense_df["amount"] > 0)
].copy()

valid_work_df = work_df[
    (work_df["task"].astype(str).str.strip() != "") |
    (work_df["materials"].astype(str).str.strip() != "") |
    (work_df["hours_or_people"].astype(str).str.strip() != "")
].copy()

if len(valid_expense_df) > 0:
    receipt_rate = (valid_expense_df["receipt"] == "Yes").mean()
    total_expense = float(valid_expense_df["amount"].sum())
else:
    receipt_rate = 1.0
    total_expense = 0.0

report_score, report_multiplier = calc_report_score(
    on_time=on_time,
    consistency=consistency,
    clarity=clarity,
    receipt_rate=receipt_rate,
)

yield_per_ha = harvest_kg / area_ha if area_ha > 0 else 0.0
base_score = yield_per_ha * land_coeff
final_score = base_score * report_multiplier

# -----------------------------
# 6. Results
# -----------------------------
st.subheader("6. Evaluation Result")
r1, r2, r3, r4 = st.columns(4)
r1.metric("Yield / ha", f"{yield_per_ha:,.2f} kg")
r2.metric("Land Coefficient", f"{land_coeff:.2f}")
r3.metric("Report Multiplier", f"{report_multiplier:.2f}")
r4.metric("Final Score", f"{final_score:,.2f}")

with st.expander("See detailed calculation"):
    st.write(f"Base Score = (Harvest / Area) × Land Coefficient")
    st.code(f"({harvest_kg:,.2f} / {area_ha:,.2f}) × {land_coeff:.2f} = {base_score:,.2f}")
    st.write("Final Score = Base Score × Report Multiplier")
    st.code(f"{base_score:,.2f} × {report_multiplier:.2f} = {final_score:,.2f}")
    st.write(f"Report Review Score: {report_score:.0f} / 100")
    st.write(f"Receipt Coverage: {receipt_rate*100:,.1f}%")

# -----------------------------
# 7. Data preview / export
# -----------------------------
st.subheader("7. Report Output")
summary_df = pd.DataFrame([
    {
        "employee_name": employee_name,
        "plot_id": plot_id,
        "report_month": report_month,
        "office": office,
        "area_ha": area_ha,
        "monthly_harvest_kg": harvest_kg,
        "cumulative_harvest_kg": cumulative_harvest_kg,
        "yield_per_ha": yield_per_ha,
        "land_difficulty": land_difficulty,
        "land_coefficient": land_coeff,
        "weather_notes": weather_notes,
        "issues": issues,
        "actions_next_month": actions,
        "submitted_on_time": on_time,
        "consistency": consistency,
        "clarity": clarity,
        "receipt_rate": receipt_rate,
        "report_score": report_score,
        "report_multiplier": report_multiplier,
        "base_score": base_score,
        "final_score": final_score,
        "total_expense": total_expense,
        "work_log_count": len(valid_work_df),
        "expense_count": len(valid_expense_df),
    }
])

st.dataframe(summary_df, use_container_width=True)

col1, col2 = st.columns(2)
with col1:
    csv_data = summary_df.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        label="Download Summary CSV",
        data=csv_data,
        file_name=f"monthly_report_summary_{employee_name or 'employee'}_{report_month}.csv",
        mime="text/csv",
    )
with col2:
    excel_bytes = to_excel_bytes(summary_df, valid_work_df, valid_expense_df)
    st.download_button(
        label="Download Excel Report",
        data=excel_bytes,
        file_name=f"monthly_report_{employee_name or 'employee'}_{report_month}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

st.markdown("---")
st.caption(
    "Next step candidates: bilingual UI, receipt image upload, monthly master list, manager approval flow, Supabase save, and ranking dashboard."
)
