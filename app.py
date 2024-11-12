import streamlit as st
import pandas as pd
import numpy as np 
import time
import altair as alt
from altair import Chart, X, Y


# Load the dataframe
df = pd.read_csv('cowboys_24-25.csv')

# Create separate DataFrames by position
for pos in df['POS'].unique():
    globals()[f"df_{pos}"] = df[df['POS'] == pos]

# Convert CAP HIT to float
df['CAP HIT'] = df['CAP HIT'].astype(float)
df['DEAD CAP'] = df['DEAD CAP'].astype(float)
pos_cap_hit = df.groupby('POS')['CAP HIT'].sum()

# DataFrame for Position Cap vs Dead Cap
new_cap_deadcap = df[['CAP HIT', 'DEAD CAP', 'POS']]
pos_cap_deadcap = new_cap_deadcap.groupby('POS').sum()

pos_fa_cap = pd.DataFrame({
    'cap_hit': [df]
})

# print(pos_cap_hit)

# Separate based on position categories
offense_cap_hit = pos_cap_hit.loc[['C', 'G', 'LT', 'QB', 'RB', 'RT', 'TE', 'WR', 'FB']].to_frame()
# offense_cap_hit['TOTAL'] = offense_cap_hit.sum()
defense_cap_hit = pos_cap_hit.loc[['CB', 'DE', 'DT', 'FS', 'ILB', 'S', 'OLB']].to_frame()
# defense_cap_hit['TOTAL'] = defense_cap_hit.sum()
special_cap_hit = pos_cap_hit.loc[['K', 'P', 'LS']].to_frame()
# special_cap_hit['TOTAL'] = special_cap_hit.sum()

# print(offense_cap_hit)

# Total team cap and side of the ball totals
team_cap_hit = pd.DataFrame({
    'team': ['team total', 'offense', 'defense', 'special'],
    'total': [df['CAP HIT'].sum(), offense_cap_hit['CAP HIT'].sum(), defense_cap_hit['CAP HIT'].sum(), special_cap_hit['CAP HIT'].sum()]
})
# print(team_cap_hit)
st.title('Dallas Cowboys 24-25 Compared to league Avg')
st.markdown('These are all graphs that help explain the Salary Cap Table for the NFLs Dallas Cowboys. Here I will be breaking down different parts of the teams structure, strengths, weaknesses, liabilities, and points for improvement')

# TODO: 
#################################### 
# Bar Graph for SOB Spending       # 
####################################

sob_bars = (
    alt.Chart(team_cap_hit, title="Sides of the Ball Spending")
    .mark_bar()
    .encode(
        x=alt.X("team", axis=alt.Axis(title="Teams"), sort="-x"),
        y=alt.Y("total", axis=alt.Axis(title="Totals")),
        color=alt.Color("total"),
    )
    .properties(width=650, height=400)
)

sob_bar_plot = st.altair_chart(sob_bars)

# TODO:
#################################### 
# AVV by POS vs League Avg AVV POV # 
####################################

# Sort `dal_pos_avg` by AAV in descending order before plotting
dal_pos_avg = pd.DataFrame({
    'pos': ['QB', 'RB', 'WR', 'TE', 'OL', 'DL', 'LB', 'SEC', 'K', 'P', 'LS'],
    'aav': [76.03, 4.92, 67.54, 4.75, 56.97, 36.19, 11.47, 46.49, 0.9, 3.0, 1.29]
}).sort_values(by='aav', ascending=False)

# Sort `lg_pos_avg` by the same order to match
lg_pos_avg = pd.DataFrame({
    'pos': ['QB', 'RB', 'WR', 'TE', 'OL', 'DL', 'LB', 'SEC', 'K', 'P', 'LS'],
    'aav': [41.01, 11.5, 41.31, 13.96, 57.91, 50.56, 34.39, 45.96, 3.94, 2.1, 1.39]
}).set_index('pos').loc[dal_pos_avg['pos']].reset_index()

st.markdown('This first chart shows Dallas position AAV (Average Annual Value) compared to the league Avg (Red Tick) AAV is the average value of a players contract over the full years of the contract length')

# Bar chart for team AAV by position (sorted)
aav_bar = alt.Chart(dal_pos_avg).mark_bar().encode(
    x=alt.X("pos", axis=alt.Axis(title="Positions"), sort=dal_pos_avg['pos'].tolist()),
    y=alt.Y("aav", axis=alt.Axis(title="AAV ($mm vs League Avg)")),
    color=alt.value("steelblue")  # Optional: Color the bars
).properties(
    title='AVV by Position vs League Avg',
    width=alt.Step(40)  # Controls width of each bar
)

# Tick mark for league average AAV by position
aav_tick = alt.Chart(lg_pos_avg).mark_tick(
    color='red',
    thickness=2,
    size=40 * 0.9  # Controls width of tick
).encode(
    x=alt.X("pos", axis=alt.Axis(title="Positions"), sort=dal_pos_avg['pos'].tolist()),
    y=alt.Y("aav", axis=alt.Axis(title="AAV ($mm vs League Avg)"))
)

# Combine the bar and tick charts
aav_combined_chart = aav_bar + aav_tick

aav_bar_tick = st.altair_chart(aav_combined_chart)


# TODO:
#################################### 
# Layered Bar Cap Hit vs Dead Cap  # 
####################################


long_format_df = df.melt(id_vars=['POS'], value_vars=['CAP HIT', 'DEAD CAP'])
# print(long_format_df[long_format_df['POS'] == 'QB'])

layered =alt.Chart(long_format_df).mark_bar(opacity=0.7).encode(
        x='POS',
        y='value:Q',
        color='variable'
).properties(
    title='Cap Hit vs Dead Cap by Position'
)

layered_bar = st.altair_chart(layered)
st.markdown('This graph above presents a comprehensive analysis of the cap hit associated with the quarterback position, specifically highlighting the Cap Hit with the Dead Cap Hit. The substantial liability focused at the quarterback position due to the Prescott contract shows the teams quarterback situation and the significant financial burden it could face in the future.')


# TODO:
#################################### 
# Number of FAs per year           # 
####################################

free_agent_counts = df.groupby('FREE AGENT YEAR').size().reset_index(name='Count')

fa_chart = alt.Chart(free_agent_counts).mark_bar().encode(
    x=alt.X('FREE AGENT YEAR:O', title='Free Agent Year', sort='ascending'),
    y=alt.Y('Count:Q', title='Number of Players')
).properties(
    title='Number of Players by Free Agent Year'
)

fa_text = fa_chart.mark_text(
    align='center',
    baseline='bottom',
    color='white',
    dy=-3  # Adjust the position above the bar
).encode(
    text=alt.Text('Count:Q', format='.0f')  # Show player count
)

final_chart = fa_chart + fa_text

st.altair_chart(final_chart, use_container_width=True)


# TODO:
#################################### 
# Total Cap Hit by Free Agent Year # 
####################################

cap_hit_sum = df.groupby('FREE AGENT YEAR')['CAP HIT'].sum().reset_index()

cap_hit_sum['CAP HIT MM'] = (cap_hit_sum['CAP HIT'] / 1_000_000).round(2)

chart = alt.Chart(cap_hit_sum).mark_bar().encode(
    x=alt.X('FREE AGENT YEAR:O', title='Free Agent Year', sort='ascending'),
    y=alt.Y('CAP HIT MM:Q', title='Total Cap Hit (MM$)'),
    tooltip=[
        alt.Tooltip('FREE AGENT YEAR:O', title='Free Agent Year'),
        alt.Tooltip('CAP HIT MM:Q', title='Cap Hit (MM$)', format='$.2f')
    ]
).properties(
    title='Total Cap Hit by Free Agent Year',
    width=600,
    height=400
)

text = alt.Chart(cap_hit_sum).mark_text(
    align='center',
    baseline='bottom',
    color='white',
    dy=-5  # Slightly above the bar
).encode(
    x='FREE AGENT YEAR:O',
    y='CAP HIT MM:Q',
    text=alt.Text('CAP HIT MM:Q', format='$.2f')
)

final_chart = chart + text

st.altair_chart(final_chart, use_container_width=True)

