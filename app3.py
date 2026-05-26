# =========================================================
# GLOBAL DEBT ANALYSIS DASHBOARD
# STREAMLIT + POSTGRESQL
# =========================================================

import streamlit as st
import pandas as pd
import psycopg2
import plotly.express as px

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="INTERNATIONAL DEBT ANALYSIS",
    page_icon="🌍",
    layout="wide"
)

# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown("""
<style>

.main {
    background-color: #f7d4e5;
}

section[data-testid="stSidebar"] {
    background-color: #d9b3c6;
}

h1, h2, h3 {
    color: purple;
    font-weight: bold;
}

div[data-testid="metric-container"] {
    background-color: white;
    border: 3px solid purple;
    padding: 15px;
    border-radius: 10px;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# LOAD DATA FROM POSTGRESQL
# =========================================================

@st.cache_data
def load_data():

    conn = psycopg2.connect(
        host="localhost",
        database="idb",
        user="postgres",
        password="Sathdiv",
        port="5432"
    )

    query = "SELECT * FROM country_debt_data"

    df = pd.read_sql(query, conn)

    conn.close()

    return df

# =========================================================
# LOAD DATA
# =========================================================

df = load_data()

# =========================================================
# CLEAN COLUMN NAMES
# =========================================================

df.columns = df.columns.str.lower().str.strip()

# =========================================================
# DETECT COLUMN NAMES
# =========================================================

# COUNTRY COLUMN
if "country_name" in df.columns:
    country_col = "country_name"

elif "country" in df.columns:
    country_col = "country"

else:
    st.error("Country column not found")
    st.stop()

# YEAR COLUMN
if "year" in df.columns:
    year_col = "year"

else:
    st.error("Year column not found")
    st.stop()

# VALUE COLUMN
if "value" in df.columns:
    value_col = "value"

elif "debt" in df.columns:
    value_col = "debt"

else:
    st.error("Value column not found")
    st.stop()

# INDICATOR COLUMN
if "indicator_name" in df.columns:
    indicator_col = "indicator_name"

elif "series_name" in df.columns:
    indicator_col = "series_name"

elif "indicator_code" in df.columns:
    indicator_col = "indicator_code"

elif "series_code" in df.columns:
    indicator_col = "series_code"

else:
    st.error("Indicator column not found")
    st.stop()

# =========================================================
# CONVERT VALUE COLUMN TO NUMERIC
# =========================================================

df[value_col] = pd.to_numeric(
    df[value_col],
    errors="coerce"
)

df = df.dropna(subset=[value_col])

# =========================================================
# SIDEBAR NAVIGATION
# =========================================================

st.sidebar.title("🌍 GLOBAL DEBT DASHBOARD")

page = st.sidebar.radio(
    "GO TO",
    [
        "GLOBAL DEBT OVERVIEW",
        "DEBT TREND ANALYSIS",
        "GEOGRAPHIC MAPS",
        "REGIONAL DEBT INSIGHTS",
        "DEBT DISTRIBUTION",
        "SQL QUERIES"
    ]
)

# =========================================================
# FILTERS
# =========================================================

st.sidebar.header("🔍 FILTERS")

country_filter = st.sidebar.multiselect(
    "SELECT COUNTRY",
    options=sorted(df[country_col].dropna().unique())
)

year_filter = st.sidebar.multiselect(
    "SELECT YEAR",
    options=sorted(df[year_col].dropna().unique())
)

# =========================================================
# APPLY FILTERS
# =========================================================

filtered_df = df.copy()

if country_filter:
    filtered_df = filtered_df[
        filtered_df[country_col].isin(country_filter)
    ]

if year_filter:
    filtered_df = filtered_df[
        filtered_df[year_col].isin(year_filter)
    ]

# =========================================================
# GLOBAL DEBT OVERVIEW
# =========================================================

if page == "GLOBAL DEBT OVERVIEW":

    st.title("📊 GLOBAL DEBT OVERVIEW")

    total_countries = filtered_df[country_col].nunique()

    total_indicators = filtered_df[indicator_col].nunique()

    total_debt = filtered_df[value_col].sum()

    average_debt = filtered_df[value_col].mean()

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "TOTAL COUNTRIES",
        total_countries
    )

    col2.metric(
        "TOTAL INDICATORS",
        total_indicators
    )

    col3.metric(
        "TOTAL GLOBAL DEBT",
        f"{total_debt:,.2f}"
    )

    col4.metric(
        "AVERAGE DEBT",
        f"{average_debt:,.2f}"
    )

    st.divider()

    # TOP 10 COUNTRIES

    st.subheader("TOP 10 COUNTRIES BY TOTAL DEBT")

    top10 = (
        filtered_df
        .groupby(country_col)[value_col]
        .sum()
        .reset_index()
        .sort_values(by=value_col, ascending=False)
        .head(10)
    )

    fig1 = px.bar(
        top10,
        x=value_col,
        y=country_col,
        orientation="h",
        text_auto=True,
        color=value_col
    )

    st.plotly_chart(
        fig1,
        use_container_width=True
    )

    # DATA PREVIEW

    st.subheader("DATASET PREVIEW")

    st.dataframe(
        filtered_df.head(100),
        use_container_width=True
    )

# =========================================================
# DEBT TREND ANALYSIS
# =========================================================

elif page == "DEBT TREND ANALYSIS":

    st.title("📈 DEBT TREND ANALYSIS")

    yearly_trend = (
        filtered_df
        .groupby(year_col)[value_col]
        .sum()
        .reset_index()
    )

    fig2 = px.line(
        yearly_trend,
        x=year_col,
        y=value_col,
        markers=True,
        title="GLOBAL DEBT TREND OVER YEARS"
    )

    st.plotly_chart(
        fig2,
        use_container_width=True
    )

    # COUNTRY VS YEAR

    st.subheader("COUNTRY VS YEAR ANALYSIS")

    scatter_df = (
        filtered_df
        .groupby([country_col, year_col])[value_col]
        .sum()
        .reset_index()
    )

    fig4 = px.scatter(
        scatter_df,
        x=year_col,
        y=value_col,
        color=country_col,
        size=value_col,
        hover_name=country_col
    )

    st.plotly_chart(
        fig4,
        use_container_width=True
    )

# =========================================================
# GEOGRAPHIC MAPS
# =========================================================

elif page == "GEOGRAPHIC MAPS":

    st.title("🗺 GEOGRAPHIC MAPS")

    country_map = (
        filtered_df
        .groupby(country_col)[value_col]
        .sum()
        .reset_index()
    )

    fig_map = px.choropleth(
        country_map,
        locations=country_col,
        locationmode="country names",
        color=value_col,
        hover_name=country_col,
        color_continuous_scale="Reds",
        title="COUNTRY-WISE DEBT DISTRIBUTION"
    )

    st.plotly_chart(
        fig_map,
        use_container_width=True
    )

# =========================================================
# REGIONAL DEBT INSIGHTS
# =========================================================

elif page == "REGIONAL DEBT INSIGHTS":

    st.title("🌎 REGIONAL DEBT INSIGHTS")

    regional_data = (
        filtered_df
        .groupby(country_col)[value_col]
        .sum()
        .reset_index()
        .sort_values(by=value_col, ascending=False)
        .head(15)
    )

    fig_region = px.bar(
        regional_data,
        x=country_col,
        y=value_col,
        color=value_col,
        title="REGIONAL DEBT INSIGHTS"
    )

    st.plotly_chart(
        fig_region,
        use_container_width=True
    )

    # TREEMAP

    st.subheader("TREEMAP ANALYSIS")

    fig_tree = px.treemap(
        regional_data,
        path=[country_col],
        values=value_col,
        color=value_col
    )

    st.plotly_chart(
        fig_tree,
        use_container_width=True
    )

# =========================================================
# DEBT DISTRIBUTION
# =========================================================

elif page == "DEBT DISTRIBUTION":

    st.title("📉 DEBT DISTRIBUTION")

    indicator_data = (
        filtered_df
        .groupby(indicator_col)[value_col]
        .sum()
        .reset_index()
        .sort_values(by=value_col, ascending=False)
        .head(10)
    )

    # PIE CHART

    fig3 = px.pie(
        indicator_data,
        names=indicator_col,
        values=value_col,
        hole=0.4
    )

    st.plotly_chart(
        fig3,
        use_container_width=True
    )

    # HISTOGRAM

    st.subheader("DEBT HISTOGRAM")

    fig_hist = px.histogram(
        filtered_df,
        x=value_col,
        nbins=50
    )

    st.plotly_chart(
        fig_hist,
        use_container_width=True
    )

    # BOX PLOT

    st.subheader("BOXPLOT ANALYSIS")

    fig_box = px.box(
        filtered_df,
        y=value_col
    )

    st.plotly_chart(
        fig_box,
        use_container_width=True
    )

# =========================================================
# SQL QUERIES PAGE
# =========================================================

elif page == "SQL QUERIES":

    st.title("🗄 SQL ANALYTICAL QUESTIONS")

    queries = {

    # 🔹 BASIC LEVEL

    "1. DISTINCT COUNTRY NAMES":
    """
    SELECT DISTINCT country_name
    FROM country_debt_data;
    """,

    "2. COUNT TOTAL COUNTRIES":
    """
    SELECT COUNT(DISTINCT country_name) AS total_countries
    FROM country_debt_data;
    """,

    "3. TOTAL NUMBER OF INDICATORS":
    """
    SELECT COUNT(DISTINCT series_name) AS total_indicators
    FROM country_debt_data;
    """,

    "4. FIRST 10 RECORDS":
    """
    SELECT *
    FROM country_debt_data
    LIMIT 10;
    """,

    "5. TOTAL GLOBAL DEBT":
    """
    SELECT SUM(value) AS total_global_debt
    FROM country_debt_data;
    """,

    "6. UNIQUE INDICATOR NAMES":
    """
    SELECT DISTINCT series_name
    FROM country_debt_data;
    """,

    "7. NUMBER OF RECORDS FOR EACH COUNTRY":
    """
    SELECT country_name,
           COUNT(*) AS total_records
    FROM country_debt_data
    GROUP BY country_name
    ORDER BY total_records DESC;
    """,

    "8. DEBT GREATER THAN 1 BILLION USD":
    """
    SELECT *
    FROM country_debt_data
    WHERE value > 1000000000;
    """,

    "9. MINIMUM MAXIMUM AND AVERAGE DEBT":
    """
    SELECT MIN(value) AS minimum_debt,
           MAX(value) AS maximum_debt,
           AVG(value) AS average_debt
    FROM country_debt_data;
    """,

    "10. TOTAL NUMBER OF RECORDS":
    """
    SELECT COUNT(*) AS total_records
    FROM country_debt_data;
    """,


    # 🔹 INTERMEDIATE LEVEL

    "11. TOTAL DEBT FOR EACH COUNTRY":
    """
    SELECT country_name,
           SUM(value) AS total_debt
    FROM country_debt_data
    GROUP BY country_name
    ORDER BY total_debt DESC;
    """,

    "12. TOP 10 COUNTRIES WITH HIGHEST TOTAL DEBT":
    """
    SELECT country_name,
           SUM(value) AS total_debt
    FROM country_debt_data
    GROUP BY country_name
    ORDER BY total_debt DESC
    LIMIT 10;
    """,

    "13. AVERAGE DEBT PER COUNTRY":
    """
    SELECT country_name,
           AVG(value) AS average_debt
    FROM country_debt_data
    GROUP BY country_name
    ORDER BY average_debt DESC;
    """,

    "14. TOTAL DEBT FOR EACH INDICATOR":
    """
    SELECT series_name,
           SUM(value) AS total_debt
    FROM country_debt_data
    GROUP BY series_name
    ORDER BY total_debt DESC;
    """,

    "15. INDICATOR WITH HIGHEST TOTAL DEBT":
    """
    SELECT series_name,
           SUM(value) AS total_debt
    FROM country_debt_data
    GROUP BY series_name
    ORDER BY total_debt DESC
    LIMIT 1;
    """,

    "16. COUNTRY WITH LOWEST TOTAL DEBT":
    """
    SELECT country_name,
           SUM(value) AS total_debt
    FROM country_debt_data
    GROUP BY country_name
    ORDER BY total_debt ASC
    LIMIT 1;
    """,

    "17. TOTAL DEBT FOR COUNTRY AND INDICATOR":
    """
    SELECT series_name,
       SUM(value) AS total_debt
    FROM country_debt_data
    GROUP BY series_name
    ORDER BY total_debt DESC
    LIMIT 5;
    """,

    "18. COUNT INDICATORS FOR EACH COUNTRY":
    """
    SELECT country_name,
           COUNT(DISTINCT series_name) AS total_indicators
    FROM country_debt_data
    GROUP BY country_name
    ORDER BY total_indicators DESC;
    """,

    "19. COUNTRIES ABOVE GLOBAL AVERAGE DEBT":
    """
    SELECT country_name,
           SUM(value) AS total_debt
    FROM country_debt_data
    GROUP BY country_name
    HAVING SUM(value) > (
        SELECT AVG(country_total)
        FROM (
            SELECT SUM(value) AS country_total
            FROM country_debt_data
            GROUP BY country_name
        ) avg_table
    )
    ORDER BY total_debt DESC;
    """,

    "20. RANK COUNTRIES BASED ON TOTAL DEBT":
    """
    SELECT country_name,
           SUM(value) AS total_debt,
           RANK() OVER(
               ORDER BY SUM(value) DESC
           ) AS debt_rank
    FROM country_debt_data
    GROUP BY country_name;
    """,


    # 🔹 ADVANCED LEVEL

    "21. TOP 5 INDICATORS CONTRIBUTING MOST TO GLOBAL DEBT":
    """
    SELECT series_name,
       SUM(value) AS total_debt
    FROM country_debt_data
    GROUP BY series_name
    ORDER BY total_debt DESC
    LIMIT 5;
    """,

    "22. PERCENTAGE CONTRIBUTION OF EACH COUNTRY":
    """
    SELECT country_name,
           SUM(value) AS total_debt,
           ROUND(
               (SUM(value) * 100.0 /
               (SELECT SUM(value)
                FROM country_debt_data)), 2
           ) AS contribution_percentage
    FROM country_debt_data
    GROUP BY country_name
    ORDER BY contribution_percentage DESC;
    """,

    "23. TOP 3 COUNTRIES FOR EACH INDICATOR":
    """
    SELECT *
    FROM (
        SELECT country_name,
               series_name,
               SUM(value) AS total_debt,
               RANK() OVER(
                   PARTITION BY series_name
                   ORDER BY SUM(value) DESC
               ) AS rank_num
        FROM country_debt_data
        GROUP BY country_name, series_name
    ) ranked_data
    WHERE rank_num <= 3;
    """,

    "24. DIFFERENCE BETWEEN MAXIMUM AND MINIMUM DEBT":
    """
    SELECT country_name,
           MAX(value) AS max_debt,
           MIN(value) AS min_debt,
           MAX(value) - MIN(value) AS debt_difference
    FROM country_debt_data
    GROUP BY country_name
    ORDER BY debt_difference DESC;
    """,

  
    "25. TOP 10 COUNTRIES VIEW DATA":
    """
    SELECT country_name,
       SUM(value) AS total_debt
    FROM country_debt_data
    GROUP BY country_name
    ORDER BY total_debt DESC
    LIMIT 10;
    """,

    "26. CATEGORIZE COUNTRIES BY DEBT":
    """
    SELECT country_name,
           SUM(value) AS total_debt,
           CASE
               WHEN SUM(value) > 1000000000
                    THEN 'High Debt'

               WHEN SUM(value)
                    BETWEEN 500000000
                    AND 1000000000
                    THEN 'Medium Debt'

               ELSE 'Low Debt'
           END AS debt_category
    FROM country_debt_data
    GROUP BY country_name;
    """,

    "27. CUMULATIVE DEBT PER COUNTRY":
    """
    SELECT country_name,
           year,
           value,
           SUM(value) OVER(
               PARTITION BY country_name
               ORDER BY year
           ) AS cumulative_debt
    FROM country_debt_data;
    """,

    "28. INDICATORS ABOVE OVERALL AVERAGE DEBT":
    """
    SELECT series_name,
           AVG(value) AS avg_indicator_debt
    FROM country_debt_data
    GROUP BY series_name
    HAVING AVG(value) > (
        SELECT AVG(value)
        FROM country_debt_data
    )
    ORDER BY avg_indicator_debt DESC;
    """,

    "29. COUNTRIES CONTRIBUTING MORE THAN 5 PERCENT":
    """
    SELECT country_name,
       SUM(value) AS total_debt,
       ROUND(
           (SUM(value) * 100.0 /
           (SELECT SUM(value)
            FROM country_debt_data)), 2
       ) AS contribution_percentage
    FROM country_debt_data
    GROUP BY country_name
    HAVING
    (SUM(value) * 100.0 /
    (SELECT SUM(value)
     FROM country_debt_data)) > 5
    ORDER BY contribution_percentage DESC;
    """,

    "30. MOST DOMINANT INDICATOR FOR EACH COUNTRY":
    """
    SELECT *
    FROM (
        SELECT country_name,
               series_name,
               SUM(value) AS total_debt,
               RANK() OVER(
                   PARTITION BY country_name
                   ORDER BY SUM(value) DESC
               ) AS rank_num
        FROM country_debt_data
        GROUP BY country_name, series_name
    ) ranked_data
    WHERE rank_num = 1;
    """
}

    # QUERY SELECTION

    selected_query = st.selectbox(
        "SELECT SQL QUERY",
        list(queries.keys())
    )

    sql_query = queries[selected_query]

    # SHOW QUERY

    st.code(sql_query, language="sql")

    # EXECUTE QUERY

    conn = psycopg2.connect(
        host="localhost",
        database="idb",
        user="postgres",
        password="Sathdiv",
        port="5432"
    )

    result = pd.read_sql(sql_query, conn)

    conn.close()

    # DISPLAY RESULT

    st.dataframe(
        result,
        use_container_width=True
    )

# =========================================================
# FOOTER
# =========================================================

st.markdown("---")

st.markdown(
    """
    <center>
    <h3 style='color:purple;'>
    🚀 GLOBAL DEBT ANALYSIS DASHBOARD USING STREAMLIT + POSTGRESQL
    </h3>
    </center>
    """,
    unsafe_allow_html=True
)