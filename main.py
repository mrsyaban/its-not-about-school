import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px

# Load data
df = pd.read_csv("data/education-indicator-long.csv")
df.columns = df.columns.str.strip()  # Clean column names
df_long = df.melt(id_vars=["Indicator"], var_name="Year", value_name="Value")
df_long["Year"] = pd.to_numeric(df_long["Year"], errors="coerce")
df_long["Value"] = pd.to_numeric(df_long["Value"], errors="coerce")

# PISA scores data
df_pisa = pd.read_csv("data/pisa-score.csv")
melted = df_pisa.melt(id_vars=["Year"], var_name="Subject", value_name="Score")

# Custom data for Pupil-Teacher ratio
data = {
    "country": [
        "Brunei Darussalam", "Singapore", "Malaysia", "Vietnam", "Indonesia",
        "Timor-Leste", "Thailand", "Myanmar", "Philippines", "Cambodia", "Laos"
    ],
    "iso_alpha": [
        "BRN", "SGP", "MYS", "VNM", "IDN", "TLS", "THA", "MMR", "PHL", "KHM", "LAO"
    ],
    "pupil_teacher_ratio_primary": [10, 15, 12, 20, 17, 27, 17, 24, 29, 42, 22]
}

df_ratio = pd.DataFrame(data)

# Streamlit Layout
st.set_page_config(page_title="Indonesia Education Progress", layout="wide")

st.markdown("""
    <style>
        /* Apply Times New Roman font to the body */
        body {
            font-family: 'Times New Roman', serif !important;
        }
        .main {
            max-width: 1200px;
            margin: 0 auto;
        }
        /* Apply font to other elements (headings, subheadings, etc.) */
        h1, h2, h3, h4, h5, h6, p {
            font-family: 'Times New Roman', serif !important;
        }
    </style>
""", unsafe_allow_html=True)

# Title and Introduction
st.title(" It’s not about school, It’s about learning")
st.markdown("""
    Despite decades of reform and policy changes on education, public perception remains skeptical. 
    News headlines and social media debates often echo the same concern: **Has our education really progressed?**
    
    Over the past 3 decades, Indonesia has significantly improved access to education, with a key turning point around 2010.
    More Indonesian children are in school today than ever before. But, access isn't the only question anymore.
    """)

# Access to Education - NER Trends with indicator selection
st.subheader("Access to Education - Net Enrollment Rate (NER) Trends")

# Year range filter
year_range = st.slider(
    "Select Year Range",
    min_value=int(df_long["Year"].min()),
    max_value=int(df_long["Year"].max()),
    value=(int(df_long["Year"].min()), int(df_long["Year"].max())),
    step=1
)

# Filter the data based on the selected year range
filtered_data = df_long[
    (df_long["Year"] >= year_range[0]) & (df_long["Year"] <= year_range[1])
]

# Select which indicators to display
selected_indicators = st.multiselect(
    "Select Indicators to Display:",
    options=df_long["Indicator"].unique(),
    default=["NER Primary Education", "NER Lower Secondaary Education", "NER Upper Secondary Education"]
)

color_mapping = {
    "NER Primary Education": "#92242a",
    "NER Lower Secondaary Education": "#4777af",
    "NER Upper Secondary Education": "#7d8c9c"
}

# Filter the data based on selected indicators
filtered_data = filtered_data[filtered_data["Indicator"].isin(selected_indicators)]

# Line chart for NER
line_chart = alt.Chart(filtered_data).mark_line(
    point=alt.OverlayMarkDef(
        filled=False,
        size=100,
        shape='circle'  # You can change to 'square', 'diamond', etc.
    ),
    strokeWidth=3,  # Thicker line
    interpolate='monotone'  # Smooth curve instead of jagged lines
).encode(
    x=alt.X("Year:O", title="Year"),
    y=alt.Y("Value:Q", title="NER", scale=alt.Scale(zero=False)),
    color=alt.Color(
        "Indicator:N",
        title="Indicator",
        scale=alt.Scale(domain=list(color_mapping.keys()), range=list(color_mapping.values()))
    ),
    tooltip=["Year", "Indicator", "Value"]
).properties(width=900, height=700).interactive()

st.altair_chart(line_chart, use_container_width=True)

# Middle Section - Pupil Teacher Ratio
st.markdown("""
    ### But then a natural question arises,  
    **If access is no longer the biggest problem, why does it still feel like there's little progress in the actual outcomes?**
    
    In a system where access is no longer the main problem, **student-teacher ratio** becomes a key indicator of learning quality.
    
    The map below shows the pupil-teacher ratio across Southeast Asia in primary education.
""")

# Pupil-Teacher Ratio Map
fig = px.choropleth(df_ratio, locations="iso_alpha", locationmode="ISO-3", color="pupil_teacher_ratio_primary",
                    hover_name="country", color_continuous_scale="Blues", labels={"pupil_teacher_ratio_primary": "Pupils per Teacher"},
                    title="Pupil-Teacher Ratio in Primary Education (Lower is Better)")

# Update map's geographical background to black
fig.update_geos(
    visible=False, 
    resolution=50, 
    showcountries=True, 
    fitbounds="locations",
    bgcolor='black'  # Set geo background to black
)

# Update the whole plot's background to black
fig.update_layout(
    margin={"r": 0, "t": 50, "l": 0, "b": 0},
    plot_bgcolor='#0e1117'  # Set plot background to black
)

st.plotly_chart(fig, use_container_width=False)

# PISA Scores
st.subheader("Indonesia PISA Scores Trends (2000-2022)")
st.markdown("""
    Indonesia’s PISA scores for **Reading**, **Mathematics**, and **Science** have been declining since their peak in 2015.
    This raises the question of whether the improvements in access to education are truly reflected in the learning outcomes.
""")
line_chart_pisa = alt.Chart(melted).mark_line().encode(
    x=alt.X("Year:O", title="Year"),
    y=alt.Y("Score:Q", title="PISA Score", scale=alt.Scale(domain=[350, 450])),
    color="Subject:N",
    tooltip=["Year", "Subject", "Score"]
).properties(width=700, height=500)
st.altair_chart(line_chart_pisa, use_container_width=True)

# Optional data table for PISA Scores
with st.expander("🔍 Show raw data for PISA Scores"):
    st.dataframe(df_pisa)

# Conclusion
st.markdown("""
    Indonesia has made commendable progress in expanding access to education, but the quality of learning remains a critical concern.
    With declining PISA scores and a high student-teacher ratio, the next challenge lies in ensuring that students not only attend school but truly learn.
""")
