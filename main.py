import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.figure_factory as ff
import plotly.graph_objects as go
from fpdf import FPDF
import os

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="VedX AI",
    page_icon="🤖",
    layout="wide"
)

# =========================================================
# CUSTOM CSS
# =========================================================
st.markdown("""
<style>
.stApp {
    background: linear-gradient(to bottom right, #020617, #0f172a, #111827);
    color: white;
}
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
.main-title {
    text-align: center;
    font-size: 75px;
    font-weight: 800;
    color: white;
    margin-top: 10px;
}
.sub-title {
    text-align: center;
    font-size: 24px;
    color: #94a3b8;
    margin-bottom: 30px;
}
.insight-box {
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 12px;
    padding: 16px 20px;
    margin-bottom: 10px;
    font-size: 15px;
    color: #e2e8f0;
}
section[data-testid="stFileUploader"] {
    background: #111827;
    border: 1px solid #374151;
    padding: 18px;
    border-radius: 18px;
}
.stTextArea textarea {
    background: #ffffff !important;
    color: #111827 !important;
    border: 2px solid #2563eb !important;
    border-radius: 16px !important;
    font-size: 17px !important;
    padding: 14px !important;
    min-height: 90px !important;
    max-height: 140px !important;
}
div.stButton > button {
    background: linear-gradient(90deg, #2563eb, #1d4ed8);
    color: white;
    border: none;
    border-radius: 12px;
    height: 50px;
    font-size: 18px;
    font-weight: 700;
    width: 220px;
}
div.stButton > button:hover {
    background: #1e40af;
}
[data-testid="metric-container"] {
    background: #111827;
    border: 1px solid #374151;
    padding: 15px;
    border-radius: 16px;
}
</style>
""", unsafe_allow_html=True)

# =========================================================
# HEADER
# =========================================================
st.markdown("<div class='main-title'>🤖 VedX AI</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>AI Data Analysis Platform</div>", unsafe_allow_html=True)

# =========================================================
# FILE UPLOAD
# =========================================================
uploaded_file = st.file_uploader(
    "📂 Upload CSV / Excel / JSON Dataset",
    type=["csv", "xlsx", "json"]
)

df = None

# =========================================================
# LOAD DATASET
# =========================================================
if uploaded_file:

    try:
        ext = uploaded_file.name.split(".")[-1].lower()

        if ext == "csv":
            df = pd.read_csv(uploaded_file)
        elif ext == "xlsx":
            df = pd.read_excel(uploaded_file)
        elif ext == "json":
            df = pd.read_json(uploaded_file)

        df = df.drop_duplicates()

        for col in df.columns:
            try:
                df[col] = pd.to_numeric(df[col])
            except:
                pass

        st.success("✅ Dataset Uploaded Successfully")

        # =====================================================
        # METRICS
        # =====================================================
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Rows", df.shape[0])
        c2.metric("Columns", df.shape[1])
        c3.metric("Missing Values", int(df.isnull().sum().sum()))
        c4.metric("Duplicate Rows", 0)

        # =====================================================
        # TABS
        # =====================================================
        tab1, tab2, tab3 = st.tabs([
            "📊 Preview",
            "🔍 Full Analysis",
            "📈 Charts"
        ])

        numeric_cols = list(df.select_dtypes(include='number').columns)
        text_cols = list(df.select_dtypes(include='object').columns)

        # --- TAB 1: PREVIEW ---
        with tab1:
            st.subheader("📊 Dataset Preview (First 10 Rows)")
            st.dataframe(df.head(10), use_container_width=True)

            st.subheader("📋 Column Information")
            col_info = pd.DataFrame({
                "Column": df.columns,
                "Data Type": df.dtypes.values,
                "Non-Null Count": df.count().values,
                "Missing Values": df.isnull().sum().values,
                "Unique Values": df.nunique().values
            })
            st.dataframe(col_info, use_container_width=True)

        # --- TAB 2: FULL ANALYSIS ---
        with tab2:
            st.subheader("🔍 Automatic Data Analysis")

            all_insights = []

            # Basic info
            st.markdown("### 📌 Dataset Overview")
            st.markdown(f"""
            <div class='insight-box'>
            📁 <b>Total Records:</b> {df.shape[0]} rows × {df.shape[1]} columns<br>
            🔢 <b>Numeric Columns:</b> {len(numeric_cols)} — {', '.join(numeric_cols[:5]) if numeric_cols else 'None'}<br>
            🔤 <b>Text Columns:</b> {len(text_cols)} — {', '.join(text_cols[:5]) if text_cols else 'None'}<br>
            ❌ <b>Missing Values:</b> {int(df.isnull().sum().sum())} total missing cells<br>
            💯 <b>Data Completeness:</b> {round((1 - df.isnull().sum().sum() / (df.shape[0] * df.shape[1])) * 100, 1)}%
            </div>
            """, unsafe_allow_html=True)

            all_insights.append(f"Dataset: {df.shape[0]} rows, {df.shape[1]} columns")
            all_insights.append(f"Data Completeness: {round((1 - df.isnull().sum().sum()/(df.shape[0]*df.shape[1]))*100,1)}%")

            # Numeric analysis
            if len(numeric_cols) > 0:
                st.markdown("### 📊 Numeric Column Analysis")

                desc = df[numeric_cols].describe().round(2)
                st.dataframe(desc, use_container_width=True)

                for col in numeric_cols[:5]:
                    avg = round(df[col].mean(), 2)
                    mx = round(df[col].max(), 2)
                    mn = round(df[col].min(), 2)
                    median = round(df[col].median(), 2)
                    std = round(df[col].std(), 2)

                    insight_text = (
                        f"<b>{col}</b> → "
                        f"Min: {mn} | Max: {mx} | "
                        f"Avg: {avg} | Median: {median} | Std Dev: {std}"
                    )
                    st.markdown(
                        f"<div class='insight-box'>{insight_text}</div>",
                        unsafe_allow_html=True
                    )
                    all_insights.append(
                        f"{col}: Min={mn}, Max={mx}, Avg={avg}, Median={median}"
                    )

            # Text/Category analysis
            if len(text_cols) > 0:
                st.markdown("### 🔤 Category Column Analysis")

                for col in text_cols[:4]:
                    top_val = df[col].value_counts().idxmax()
                    unique_count = df[col].nunique()
                    top_count = df[col].value_counts().iloc[0]
                    top_pct = round((top_count / df.shape[0]) * 100, 1)

                    insight_text = (
                        f"<b>{col}</b> → "
                        f"Unique Values: {unique_count} | "
                        f"Most Common: '{top_val}' ({top_pct}%)"
                    )
                    st.markdown(
                        f"<div class='insight-box'>{insight_text}</div>",
                        unsafe_allow_html=True
                    )
                    all_insights.append(
                        f"{col}: {unique_count} unique values, most common = '{top_val}' ({top_pct}%)"
                    )

            # Missing values detail
            missing = df.isnull().sum()
            missing = missing[missing > 0]
            if len(missing) > 0:
                st.markdown("### ⚠️ Missing Values Detail")
                missing_df = pd.DataFrame({
                    "Column": missing.index,
                    "Missing Count": missing.values,
                    "Missing %": round(missing.values / df.shape[0] * 100, 1)
                })
                st.dataframe(missing_df, use_container_width=True)
            else:
                st.markdown(
                    "<div class='insight-box'>✅ No missing values found in this dataset!</div>",
                    unsafe_allow_html=True
                )

            # Correlation
            if len(numeric_cols) >= 2:
                st.markdown("### 🔗 Correlation Analysis")
                corr = df[numeric_cols].corr().round(2)

                # Find strongest correlation
                corr_pairs = []
                for i in range(len(corr.columns)):
                    for j in range(i+1, len(corr.columns)):
                        corr_pairs.append((
                            corr.columns[i],
                            corr.columns[j],
                            corr.iloc[i, j]
                        ))

                if corr_pairs:
                    corr_pairs.sort(key=lambda x: abs(x[2]), reverse=True)
                    top_corr = corr_pairs[0]
                    direction = "positive" if top_corr[2] > 0 else "negative"
                    st.markdown(
                        f"<div class='insight-box'>💡 <b>Strongest Correlation:</b> "
                        f"'{top_corr[0]}' and '{top_corr[1]}' have a "
                        f"<b>{direction} correlation of {top_corr[2]}</b></div>",
                        unsafe_allow_html=True
                    )
                    all_insights.append(
                        f"Strongest correlation: {top_corr[0]} vs {top_corr[1]} = {top_corr[2]}"
                    )

                fig = ff.create_annotated_heatmap(
                    z=corr.values,
                    x=list(corr.columns),
                    y=list(corr.index),
                    colorscale='Blues'
                )
                st.plotly_chart(fig, use_container_width=True)

            # Save for PDF
            st.session_state["pdf_answer"] = "\n".join(all_insights)
            st.session_state["full_analysis_done"] = True

        # --- TAB 3: CHARTS ---
        with tab3:
            st.subheader("📈 Auto-Generated Charts")

            if len(numeric_cols) > 0:
                # Distribution chart for first numeric column
                st.markdown(f"**Distribution of {numeric_cols[0]}**")
                fig1 = px.histogram(
                    df,
                    x=numeric_cols[0],
                    template="plotly_dark",
                    color_discrete_sequence=["#2563eb"]
                )
                st.plotly_chart(fig1, use_container_width=True)

            if len(text_cols) > 0 and len(numeric_cols) > 0:
                # Bar chart
                st.markdown(f"**{numeric_cols[0]} by {text_cols[0]}**")
                bar_data = (
                    df.groupby(text_cols[0])[numeric_cols[0]]
                    .mean()
                    .reset_index()
                    .sort_values(numeric_cols[0], ascending=False)
                    .head(10)
                )
                fig2 = px.bar(
                    bar_data,
                    x=text_cols[0],
                    y=numeric_cols[0],
                    template="plotly_dark",
                    color_discrete_sequence=["#2563eb"],
                    title=f"Average {numeric_cols[0]} by {text_cols[0]}"
                )
                st.plotly_chart(fig2, use_container_width=True)

                # Pie chart
                st.markdown(f"**Distribution of {text_cols[0]}**")
                pie_data = (
                    df[text_cols[0]]
                    .value_counts()
                    .head(8)
                    .reset_index()
                )
                pie_data.columns = [text_cols[0], "Count"]
                fig3 = px.pie(
                    pie_data,
                    names=text_cols[0],
                    values="Count",
                    template="plotly_dark",
                    title=f"{text_cols[0]} Distribution"
                )
                st.plotly_chart(fig3, use_container_width=True)

            if len(numeric_cols) >= 2:
                # Scatter plot
                st.markdown(f"**{numeric_cols[0]} vs {numeric_cols[1]}**")
                fig4 = px.scatter(
                    df,
                    x=numeric_cols[0],
                    y=numeric_cols[1],
                    template="plotly_dark",
                    color_discrete_sequence=["#2563eb"],
                    title=f"Scatter: {numeric_cols[0]} vs {numeric_cols[1]}"
                )
                st.plotly_chart(fig4, use_container_width=True)

    except Exception as e:
        st.error(f"Dataset Error: {e}")

# =========================================================
# QUESTION INPUT
# =========================================================
st.markdown("---")
question = st.text_area(
    "💬 Ask Questions About Your Dataset",
    placeholder="""Examples:
• Top 5 records
• Bottom 5 records
• Show bar chart
• Show pie chart
• Show histogram
• Show scatter plot
• Show heatmap
• Show summary"""
)

ask = st.button("🚀 Analyze Dataset")

# =========================================================
# ANALYSIS ENGINE
# =========================================================
if ask:

    try:
        if df is None:
            st.warning("Please upload dataset first.")
            st.stop()

        if question.strip() == "":
            st.warning("Please enter a question.")
            st.stop()

        st.subheader("📈 Analysis Result")

        numeric_cols = list(df.select_dtypes(include='number').columns)
        text_cols = list(df.select_dtypes(include='object').columns)

        q = question.lower()

        if "top" in q:
            if len(numeric_cols) > 0:
                top_data = df.sort_values(by=numeric_cols[0], ascending=False).head(5)
                st.subheader("🏆 Top 5 Records")
                st.dataframe(top_data, use_container_width=True)
                fig = px.bar(top_data, x=top_data.index, y=numeric_cols[0],
                             title="Top 5 Analysis", template="plotly_dark")
                st.plotly_chart(fig, use_container_width=True)

        elif "bottom" in q:
            if len(numeric_cols) > 0:
                bottom_data = df.sort_values(by=numeric_cols[0], ascending=True).head(5)
                st.subheader("📉 Bottom 5 Records")
                st.dataframe(bottom_data, use_container_width=True)
                fig = px.bar(bottom_data, x=bottom_data.index, y=numeric_cols[0],
                             title="Bottom 5 Analysis", template="plotly_dark")
                st.plotly_chart(fig, use_container_width=True)

        elif "bar" in q or "compare" in q:
            if len(text_cols) > 0 and len(numeric_cols) > 0:
                chart_data = (df.groupby(text_cols[0])[numeric_cols[0]]
                              .mean().reset_index().head(10))
                fig = px.bar(chart_data, x=text_cols[0], y=numeric_cols[0],
                             title="Bar Chart Analysis", template="plotly_dark")
                st.plotly_chart(fig, use_container_width=True)
                st.dataframe(chart_data)

        elif "pie" in q:
            if len(text_cols) > 0:
                pie_data = df[text_cols[0]].value_counts().head(10).reset_index()
                pie_data.columns = [text_cols[0], "Count"]
                fig = px.pie(pie_data, names=text_cols[0], values="Count",
                             title="Pie Chart", template="plotly_dark")
                st.plotly_chart(fig, use_container_width=True)

        elif "histogram" in q:
            if len(numeric_cols) > 0:
                fig = px.histogram(df, x=numeric_cols[0],
                                   title="Histogram", template="plotly_dark")
                st.plotly_chart(fig, use_container_width=True)

        elif "scatter" in q:
            if len(numeric_cols) >= 2:
                fig = px.scatter(df, x=numeric_cols[0], y=numeric_cols[1],
                                 title="Scatter Plot", template="plotly_dark")
                st.plotly_chart(fig, use_container_width=True)

        elif "heatmap" in q or "correlation" in q:
            if len(numeric_cols) >= 2:
                corr = df[numeric_cols].corr()
                fig = ff.create_annotated_heatmap(
                    z=corr.values, x=list(corr.columns),
                    y=list(corr.index), colorscale='Blues'
                )
                st.plotly_chart(fig, use_container_width=True)

        elif "summary" in q:
            st.dataframe(df.describe(), use_container_width=True)

        elif "table" in q or "show" in q:
            st.dataframe(df.head(20), use_container_width=True)

        else:
            st.success("✅ Smart Dataset Analysis")
            insights = [f"Dataset: {df.shape[0]} rows, {df.shape[1]} columns."]

            for col in numeric_cols[:3]:
                avg = round(df[col].mean(), 2)
                mx = round(df[col].max(), 2)
                mn = round(df[col].min(), 2)
                insights.append(f"{col}: Avg={avg}, Max={mx}, Min={mn}")

            for col in text_cols[:2]:
                top_cat = df[col].value_counts().idxmax()
                insights.append(f"Most common in {col}: '{top_cat}'")

            st.subheader("📊 AI Insights")
            for insight in insights:
                st.markdown(
                    f"<div class='insight-box'>• {insight}</div>",
                    unsafe_allow_html=True
                )

            if len(text_cols) > 0 and len(numeric_cols) > 0:
                auto_data = (df.groupby(text_cols[0])[numeric_cols[0]]
                             .mean().reset_index().head(10))
                fig = px.bar(auto_data, x=text_cols[0], y=numeric_cols[0],
                             title="Automatic Analysis", template="plotly_dark")
                st.plotly_chart(fig, use_container_width=True)

            st.session_state["pdf_answer"] = "\n".join(insights)

    except Exception as e:
        st.error(f"Application Error: {e}")

# =========================================================
# PDF REPORT
# =========================================================
st.markdown("<br>", unsafe_allow_html=True)

if st.button("📄 Generate PDF Report"):

    try:
        if "pdf_answer" not in st.session_state:
            st.warning("Run Full Analysis tab first to generate report.")
        else:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", "B", 16)
            pdf.cell(200, 10, txt="VedX AI Analysis Report", ln=True, align='C')
            pdf.ln(5)
            pdf.set_font("Arial", size=12)
            pdf.cell(200, 8, txt="Generated by VedX AI Data Analysis Platform", ln=True, align='C')
            pdf.ln(10)
            pdf.set_font("Arial", "B", 13)
            pdf.cell(200, 8, txt="Dataset Insights:", ln=True)
            pdf.ln(4)
            pdf.set_font("Arial", size=12)

            for line in st.session_state["pdf_answer"].split("\n"):
                pdf.multi_cell(0, 8, f"• {line}")

            os.makedirs("reports", exist_ok=True)
            path = "reports/vedx_report.pdf"
            pdf.output(path)

            with open(path, "rb") as file:
                st.download_button(
                    label="⬇ Download PDF Report",
                    data=file,
                    file_name="vedx_report.pdf",
                    mime="application/pdf"
                )
            st.success("✅ PDF Report Generated!")

    except Exception as e:
        st.error(f"PDF Error: {e}")

# =========================================================
# FOOTER
# =========================================================
st.markdown("""
<hr>
<center style='color:#94a3b8;'>
VedX AI © 2026 | AI Data Analysis Platform | Built by Vedant Barge
</center>
""", unsafe_allow_html=True)