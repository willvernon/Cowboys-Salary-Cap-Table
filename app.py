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
st.subheader('These are all graphs that help explain the Salary Cap Table for the NFLs Dallas Cowboys.')
st.write('')
st.markdown('In this analysis, I will examine various aspects of the Dallas Cowboys’ team structure, identifying their strengths, weaknesses, liabilities, and areas for improvement. Specifically, I will focus on the NFL’s Dallas Cowboys’ salary cap table for the 2024-2025 season. Below, I present several concise graphs that illustrate the Cowboys’ cap spending distribution across different positions on the field. These graphs provide a visual representation of the team’s financial allocation and highlight the areas where they have invested more or less compared to other teams. Additionally, I have included graphs that display the Average Annual Value (AAV) of players’ contracts. This metric compares the average compensation paid to players by various teams to the Cowboys’ spending.')
st.write("")

st.markdown('By presenting these data, I aim to provide a comprehensive understanding of the Cowboys’ financial management practices and strategies on the business side of the game.')

st.write('')

st.divider()

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
st.markdown('The accompanying graph provides a comprehensive analysis of the cap hit associated with the quarterback position, with a specific focus on the Cap Hit with the Dead Cap Hit. The substantial liability associated with the quarterback position, as exemplified by the Prescott contract, underscores the critical role of the quarterback in a team’s success and the significant financial burden it may incur in the future.')

st.divider()

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

st.write('')
st.markdown('The Annual Average Value (AAV) of a players contract is represented in this graph, which illustrates the combined AAV for each position. The red bars indicate the league average for each position. This graph may be of paramount importance, as it demonstrates how the team aligns with the league’s performance. Given that each team is limited to the same salary cap, the need to match the league average is crucial for competitiveness.')
st.markdown('The two new contracts of CeeDee Lamb and Dak Prescott stand out significantly above the league average. Conversely, the Cowboys have several rookies with lower-than-league average AAVs due to their standout performances.')
st.markdown('At a glance, this strategy may appear feasible, as the limited contracts of the rookies allow the Cowboys to pay star players more while maintaining a competitive team. However, a closer examination reveals that 23 players on the 53-man roster are eligible for free agency in 2025, with an additional 11 in 2026. This presents a challenge, as some of these rookies, such as Micah Parsons, require substantial salary increases beyond their rookie deals.')

st.markdown('The team finds itself in a precarious position, one that many teams encounter when they overpay for a few superstar players, hoping that the skill-gap fillers they can no longer afford to pay will compensate. The final graph provides a snapshot of the total current salary cap hit for these players becoming free agents. While this figure may not be sufficient to retain the players, it is likely to be significantly higher than the current cap space of $23 million. Consequently, the Cowboys will need to consider the draft to address the gaps left by the players they will have to release through free agency.')
st.write('')
st.write('')

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

