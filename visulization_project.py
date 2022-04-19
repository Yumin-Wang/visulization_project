import pandas as pd
import numpy as np
import datetime as dt
import altair as alt
import streamlit as st


#read data
@st.cache
def load_data():
    covid = pd.read_csv("https://raw.githubusercontent.com/Yumin-Wang/visulization_project/main/owid-covid-data.csv")
    country_df = pd.read_csv('https://raw.githubusercontent.com/hms-dbmi/bmi706-2022/main/cancer_data/country_codes.csv', dtype = {'conuntry-code': str})[['Country','country-code']]
    covid = covid[['iso_code','continent','location','date','total_cases_per_million','new_cases_per_million','total_deaths_per_million','reproduction_rate','population']]
    covid['date'] = pd.to_datetime(covid['date'])
    covid = covid[(covid['date']>='2020-03-01')&(covid['date']<='2022-03-31')]
    covid['month'] = covid['date'].dt.strftime('%B')
    covid['year'] = covid['date'].dt.year
    covid['date'] = covid['date'].dt.strftime('%d')
    covid['total_cases_per_million']= covid['total_cases_per_million'].fillna(method='bfill').fillna(method='ffill')
    covid['new_cases_per_million']= covid['new_cases_per_million'].fillna(method='bfill').fillna(method='ffill')
    covid['total_deaths_per_million']= covid['total_deaths_per_million'].fillna(method='bfill').fillna(method='ffill')
    covid['reproduction_rate']= covid['reproduction_rate'].fillna(method='bfill').fillna(method='ffill')
    country_df['Country'] = country_df['Country'].replace(['United States of America','United Kingdom of Great Britain and Northern Ireland'],['United States','United Kingdom'])
    covid.rename(columns = {'location' : 'Country'}, inplace = True)
    covid = covid.merge(country_df,how='left',on='Country')
    covid.dropna(inplace=True)
    return covid

df = load_data()
df.rename(columns = {'new_cases_per_million':'New Cases per Million'}, inplace = True)


#read map background data
source = alt.topo_feature('https://cdn.jsdelivr.net/npm/vega-datasets@v1.29.0/data/world-110m.json', 'countries')

st.write("## COVID-19 Worldwide Metrics Over Time")

year=st.sidebar.radio(label='Year', options=df['year'].unique(), index=2)
subset = df[df["year"] == year]

month=st.sidebar.selectbox(label='Month', options=list(subset['month'].unique()), index=2)
subset = subset[subset["month"] == month]

covid_map_data = subset.copy()
covid_map_data=covid_map_data.groupby(['Country', 'country-code']).mean().reset_index()

continent=st.sidebar.selectbox(label='Continent', options=list(subset['continent'].unique()), index=3)
subset = subset[subset["continent"] == continent]

countries=st.sidebar.multiselect(label='Countries', options=list(subset['Country'].unique()))
subset = subset[subset["Country"].isin(countries)]

pie_data = subset.copy()
pie_data = pie_data.groupby(['Country', 'country-code']).mean().reset_index()


metric = st.sidebar.radio(label='Metrics', options=['total_cases_per_million','New Cases per Million'','total_deaths_per_million'], index=1)

#World_map
width_worldmap=600
height_worldmap=300

background = alt.Chart(source
).mark_geoshape(
    fill='#aaa',
    stroke='white'
).properties(
    width=width_worldmap,
    height=height_worldmap
).project('equirectangular')

worldmap_base =alt.Chart(source
    ).properties( 
        width=width_worldmap,
        height=height_worldmap
    ).project('equirectangular'
    ).transform_lookup(
        lookup="id",
        from_=alt.LookupData(covid_map_data, "country-code", ["Country",metric, 'population']),
    )


rate_scale = alt.Scale(domain=[covid_map_data[metric].min(), covid_map_data[metric].max()])
rate_color = alt.Color(field=metric, type="quantitative", scale=rate_scale)
chart_worldmap = background+worldmap_base.mark_geoshape(stroke="black", strokeWidth=0.15).encode(
    color=rate_color,
        tooltip=[
            
            alt.Tooltip(field=metric,type='quantitative', title=f"{metric} averged over month"),
            alt.Tooltip("Country:N", title="Country"),
        ]
    ).properties(
    title=f'World map for {metric} averaged in {month} of {year}'
)

#Trend line for metric
metric_base = alt.Chart(subset
 ).mark_line().encode(
    x='date:O',
    y=alt.Y(field=metric,type='quantitative'),
    color='Country:N'
).properties(
    width=400,
    height=300
) 

brush_metric =  alt.selection(type='interval', encodings=['x'])

metric_chart_detail = metric_base.transform_filter(brush_metric).properties(title=f"Compare {metric} in selected countries in {continent} during {month} of {year}")
metric_chart_global = metric_base.properties(height=60).add_selection(brush_metric)


#Trend line for reproduction rate
r_base = alt.Chart(subset
 ).mark_line().encode(
    x='date:O',
    y=alt.Y(field="reproduction_rate",type='quantitative'),
    color='Country:N'
).properties(
    width=400,
    height=300
) 

brush_r =  alt.selection(type='interval', encodings=['x'])
r_chart_detail = r_base.transform_filter(brush_r).properties(title=f"Compare reproduction rate in selected countries in {continent} during {month} of {year}")
r_chart_global = r_base.properties(height=60).add_selection(brush_r)


#Pie chart
donut = alt.Chart(pie_data).mark_arc(innerRadius=50, outerRadius=90).encode(
    theta=alt.Theta(field=metric, type="quantitative"),
    color=alt.Color(field="Country", type="nominal"),
    tooltip=[
            alt.Tooltip(field=metric, type="quantitative", title=f"{metric} averaged over month"),
            alt.Tooltip("Country:N", title="Country")]
            ).properties(width=250,title=f'Pie chart for {metric} averaged in {month} of {year} for selected countries in {continent} ')


chart_trend=alt.hconcat(metric_chart_detail&metric_chart_global, r_chart_detail&r_chart_global).resolve_scale(color='independent')

chart_trend_worldmap=alt.vconcat(chart_trend, chart_worldmap).resolve_scale(color='independent')

chart_final = alt.vconcat(chart_trend_worldmap, donut).resolve_scale(color='independent')

st.altair_chart(chart_final, use_container_width=True)





#st.altair_chart(metric_chart_detail&metric_chart_global, use_container_width=True)
#st.altair_chart(chart_worldmap, use_container_width=True)
#st.altair_chart(donut, use_container_width=True)









