"""HW6 learning scaffold. Adapt the code and complete your own report before submitting."""

import altair as alt
import pandas as pd
import streamlit as st

PLOT1_WRITEUP = """
The scatterplot diagram compares inventory record data with median recorded floor area across counties.
In the default view, Cook County has 514 records with a median area of 2,985 square feet, while Champaign has 409 records with a median of 7,501 square feet.
This illustrates that more records do not mean a larger median floor area.
Each circle represents a group from the county field, including the "Statewide" and "Unknown" categories.
The horizontal axis used linear count scale, while vertical axis accommodates the wide range of median areas using logarithmic.
Constant point size and blue color keep user's attention on position.
The agency selector and year slider allow users to recalculate both measures for the selected records.
I would add a measure of variation within the county if possible in the future, since a median hides differences among individual records.
"""

PLOT2_WRITEUP = """
This histogram highlights the construction year distribution of the selected records.
In the default view, 1970s contain the most records, with 1430, followed by 1980s with 1358.
10-years bins summarize the distribution without displaying a separate bar for every year.
Horizontal axis have chronological spacing, including decades with no selected records,
and linear vertical axis begins at 0 so bar heights accurately represent counts.
Green color avoids confusing categories.
The agency and year controls can update this chart together with the scatterplot;
when the slider choose a decade, its bar includes only the selected years.
This graph describes recorded inventory rather than all historical construction in Illinois.
With more time, I would add a bin-width selector to compare 5, 10, and 20 years intervals.
"""

HW5_COMPARISON = """
My HW5 used the BFRO reports dataset to present a horizontal bar chart of the top 15 states by report count 
and also a season classification heatmap with state dropdown.
This assignment HW6 used the Illinois building inventory dataset. 
It presents a scatterplot of county-level record counts and median floor area, together with a construction and decade histogram.
The dataset, variables, chart types, and analytical questions are differ from HW5.
"""

DATA_URL = (
    "https://raw.githubusercontent.com/UIUC-iSchool-DataViz/"
    "is445_data/main/building_inventory.csv"
)

st.set_page_config(page_title="Illinois Building Inventory", layout="centered")
st.title("Exploring Illinois Building Inventory Records")
st.write(
    "1. Compare county-level record counts and median recorded floor area."
    "2. Explore the distribution of construction decades. "
    "You can change the agency and year controls to update both charts."
)
st.markdown(f"Data source: [IS 445 building inventory CSV]({DATA_URL}).")


@st.cache_data
def load_data():
    raw = pd.read_csv(DATA_URL)
    df = raw[["Agency Name", "County", "Year Constructed", "Square Footage"]].copy()
    df["Year Constructed"] = pd.to_numeric(df["Year Constructed"], errors="coerce")
    df["Square Footage"] = pd.to_numeric(df["Square Footage"], errors="coerce")
    df = df.loc[
        (df["Year Constructed"] > 0) & (df["Square Footage"] > 0)
    ].copy()
    df["Year Constructed"] = df["Year Constructed"].astype(int)
    df["County"] = df["County"].fillna("Unknown")
    df["Agency Name"] = df["Agency Name"].fillna("Unknown")
    return raw, df


raw, df = load_data()
st.caption(
    f"{len(raw):,} raw sourcerecords; {len(df):,} have verified construction year "
    f"and recorded floor area. therefore {len(raw) - len(df):,} records are excluded "
    "from both charts."
)

st.subheader("Choose a subset")
agencies = sorted(df["Agency Name"].unique().tolist())
selected_agencies = st.multiselect(
    "Agency (leave empty for all agencies)", options=agencies, default=[]
)
first_year = int(df["Year Constructed"].min())
last_year = int(df["Year Constructed"].max())
year_range = st.slider(
    "Construction year range (inclusive)",
    min_value=first_year,
    max_value=last_year,
    value=(first_year, last_year),
)

filtered = df.loc[
    df["Year Constructed"].between(year_range[0], year_range[1])
].copy()
if selected_agencies:
    filtered = filtered.loc[filtered["Agency Name"].isin(selected_agencies)].copy()

st.write(f"**Records in the selected subset: {len(filtered):,}**")
if filtered.empty:
    st.info("No records match this subset. Select another agency or a wider year range.")

# Keep the report visible even when the selected subset is empty.
st.subheader("1. County record counts and median floor area")
if not filtered.empty:
    county_summary = (
        filtered.groupby("County", as_index=False)
        .agg(
            Records=("Square Footage", "size"),
            Median_sq_ft=("Square Footage", "median"),
        )
    )
    scatter = (
        alt.Chart(county_summary)
        .mark_circle(size=85, opacity=0.8, color="#31688e")
        .encode(
            x=alt.X("Records:Q", title="Inventory records in county", scale=alt.Scale(zero=True)),
            y=alt.Y(
                "Median_sq_ft:Q",
                title="Median recorded floor area (sq ft; log scale)",
                scale=alt.Scale(type="log", zero=False),
            ),
            tooltip=[
                alt.Tooltip("County:N"),
                alt.Tooltip("Records:Q", format=",d"),
                alt.Tooltip("Median_sq_ft:Q", title="Median sq ft", format=",.0f"),
            ],
        )
        .properties(height=350)
        .configure_axis(labelFontSize=12, titleFontSize=13)
        .configure_view(stroke=None)
    )
    st.altair_chart(scatter, use_container_width=True)
    st.caption(
        "Each point in the graph represents a county in the selected subset. Median floor area is calculated "
        "across its records. So, equal vertical distances on a log axis represent equal ratios."
    )
    with st.expander("View county summary table"):
        st.dataframe(county_summary, use_container_width=True)

if PLOT1_WRITEUP.strip():
    st.markdown(PLOT1_WRITEUP)
else:
    st.info(

    )

st.subheader("2. Construction decades in the selected subset")
if not filtered.empty:
    filtered["Decade"] = (filtered["Year Constructed"] // 10) * 10
    decade_index = range((year_range[0] // 10) * 10, (year_range[1] // 10) * 10 + 1, 10)
    decade_counts = (
        filtered.groupby("Decade").size()
        .reindex(decade_index, fill_value=0)
        .rename_axis("Decade")
        .reset_index(name="Records")
    )
    decade_counts["End"] = decade_counts["Decade"] + 10
    decade_counts["Decade_label"] = decade_counts["Decade"].astype(str) + "s"
    histogram = (
        alt.Chart(decade_counts)
        .mark_bar(color="#238b6b")
        .encode(
            x=alt.X(
                "Decade:Q", bin="binned", title="Construction decade",
                axis=alt.Axis(format="d"),
                scale=alt.Scale(zero=False, nice=False),
            ),
            x2="End:Q",
            y=alt.Y("Records:Q", title="Inventory records", scale=alt.Scale(zero=True)),
            tooltip=[
                alt.Tooltip("Decade_label:N", title="Decade"),
                alt.Tooltip("Records:Q", format=",d"),
            ],
        )
        .properties(height=320)
        .configure_axis(labelFontSize=12, titleFontSize=13)
        .configure_view(stroke=None)
    )
    st.altair_chart(histogram, use_container_width=True)
    st.caption(
        "Each bin covers 10 years. "
        "If the year slider cuts through a decade, that bar counts only the selected years. "
    )
    with st.expander("View decade summary table"):
        st.dataframe(decade_counts[["Decade_label", "Records"]], use_container_width=True)

if PLOT2_WRITEUP.strip():
    st.markdown(PLOT2_WRITEUP)
else:
    st.info(

    )

st.subheader("Relationship to Homework 5")
if HW5_COMPARISON.strip():
    st.markdown(HW5_COMPARISON)
else:
    st.info(
        
    )
