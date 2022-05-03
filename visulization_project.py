import pandas as pd
import numpy as np
import datetime as dt
from datetime import date
import altair as alt
import streamlit as st
import datetime


#read data and define variables
@st.cache
def load_data():
    covid = pd.read_csv("https://raw.githubusercontent.com/Yumin-Wang/visulization_project/main/owid-covid-data.csv")
    country_df = pd.read_csv('https://raw.githubusercontent.com/hms-dbmi/bmi706-2022/main/cancer_data/country_codes.csv', dtype = {'conuntry-code': str})[['Country','country-code']]
    covid = covid[['iso_code','continent','location','date','total_cases_per_million','new_cases_per_million','total_deaths_per_million','reproduction_rate','population',
    'median_age','handwashing_facilities','hospital_beds_per_thousand', 'total_vaccinations','life_expectancy','diabetes_prevalence','female_smokers','male_smokers']]
    covid['date'] = pd.to_datetime(covid['date'])
    covid = covid[(covid['date']>='2020-03-01')&(covid['date']<='2022-03-31')]
    covid['month'] = covid['date'].dt.strftime('%B')
    covid['year'] = covid['date'].dt.year
    covid['date'] = covid['date'].dt.strftime('%d')
    covid['total_cases_per_million']= covid['total_cases_per_million'].fillna(method='bfill').fillna(method='ffill')
    covid['new_cases_per_million']= covid['new_cases_per_million'].fillna(method='bfill').fillna(method='ffill')
    covid['total_deaths_per_million']= covid['total_deaths_per_million'].fillna(method='bfill').fillna(method='ffill')
    covid['population']=covid['population'].fillna(method='bfill').fillna(method='ffill')
    covid['reproduction_rate']= covid['reproduction_rate'].fillna(method='bfill').fillna(method='ffill')
    country_df['Country'] = country_df['Country'].replace(['United States of America','United Kingdom of Great Britain and Northern Ireland'],['United States','United Kingdom'])
    covid['median_age'] = covid['median_age'].fillna(method='bfill').fillna(method='ffill')
    covid['handwashing_facilities'] = covid['handwashing_facilities'].fillna(method='bfill').fillna(method='ffill')
    covid['hospital_beds_per_thousand'] = covid['hospital_beds_per_thousand'].fillna(method='bfill').fillna(method='ffill')
    covid['life_expectancy'] = covid['life_expectancy'].fillna(method='bfill').fillna(method='ffill')
    covid['total_vaccinations'] = covid['total_vaccinations'].fillna(0)
    #covid['diabetes_prevalance'] = covid['diabetes_prevalance'].fillna(method='bfill').fillna(method='ffill')
    covid['female_smokers'] = covid['female_smokers'].fillna(method='bfill').fillna(method='ffill')
    covid['male_smokers'] = covid['male_smokers'].fillna(method='bfill').fillna(method='ffill')


#rename columns, merge with country dataframe
    covid.rename(columns = {'location' : 'Country'}, inplace = True)
    covid = covid.merge(country_df,how='left',on='Country')
    covid.dropna(inplace=True)
    return covid

#call load datafunction
df = load_data()


#read map background data
source = alt.topo_feature('https://cdn.jsdelivr.net/npm/vega-datasets@v1.29.0/data/world-110m.json', 'countries')

#Title of page
st.write("## COVID-19 Worldwide Metrics Over Time")

#make year slider
year=st.sidebar.slider(label='Year', min_value=min(df['year']), max_value=max(df['year']), step=1, value=min(df['year']))
subset = df[df["year"] == year]

#make month select box
format='MMM'
month=st.sidebar.selectbox(label='Month', options=list(subset['month'].unique()), index=2)

#subset by month selected                                   
subset = subset[subset["month"] == month]

#subset & group for country selections
covid_map_data = subset.copy()
covid_map_data=covid_map_data.groupby(['Country', 'country-code']).mean().reset_index()

#make country multiselect
countries=st.sidebar.multiselect(label='Countries', options=list(subset['Country'].unique()), default=['China','United States','United Kingdom','South Africa'])
subset = subset[subset["Country"].isin(countries)]

#subset country
bar_data = subset.copy()
bar_data = bar_data.groupby(['Country', 'country-code']).mean().reset_index()

#make radio buttons select for metric
metric = st.sidebar.radio(label='Metrics', options=['total_cases_per_million','new_cases_per_million','total_deaths_per_million'], index=1)
metric_title = metric.replace('_', ' ')

#World_map layout
width_worldmap=600
height_worldmap=300

selector = alt.selection_single(
    on="click")

#fill in worldmap
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
    ).add_selection(
        selector
    ).transform_lookup(
        lookup="id",
        from_=alt.LookupData(covid_map_data, "country-code", ["Country",metric, 'population']),
    ).transform_filter(
        selector
    )

rate_scale = alt.Scale(domain=[covid_map_data[metric].min(), covid_map_data[metric].max()])
rate_color = alt.Color(field=metric, type="quantitative", scale=rate_scale)
chart_worldmap = background+worldmap_base.mark_geoshape(stroke="black", strokeWidth=0.15).encode(
    color=rate_color,
        tooltip=[
            alt.Tooltip(field=metric,type='quantitative'),
            alt.Tooltip("Country:N", title="Country"),
        ]
    ).properties(
    title=f'World map for {metric_title} averaged in {month} of {year}'
)

#Trend line for metric
metric_base = alt.Chart(subset
 ).mark_line().encode(
    x=alt.X('date:O', title='Date'),
    y=alt.Y(field=metric,type='quantitative', title=metric.replace('_', ' ').title()),
    color='Country:N'
).properties(
    width=400,
    height=300
) 
#add brushing to x axis slections
brush_metric =  alt.selection(type='interval', encodings=['x'])

metric_chart_detail = metric_base.transform_filter(brush_metric).properties(title=f"Compare {metric_title} in selected countries in during {month} of {year}")
metric_chart_global = metric_base.properties(height=60).add_selection(brush_metric)


#Trend line for reproduction rate
r_base = alt.Chart(subset
 ).mark_line().encode(
    x=alt.X('date:O', title='Date'),
    y=alt.Y(field="reproduction_rate",type='quantitative', title='Reproduction Rate'),
    color='Country:N'
).properties(
    width=400,
    height=300
) 
#brushing for x axis selection
brush_r =  alt.selection(type='interval', encodings=['x'])
r_chart_detail = r_base.transform_filter(brush_r).properties(title=f"Compare reproduction rate in selected countries in during {month} of {year}")
r_chart_global = r_base.properties(height=60).add_selection(brush_r)


#Bar chart for metric
bar = alt.Chart(bar_data).mark_bar().encode(
    y=alt.Y(field=metric, type="quantitative"),
    x=alt.X(field="Country", type="nominal"),
    color='Country:N',
    tooltip=[
            alt.Tooltip(field=metric, type="quantitative"),
            alt.Tooltip("Country:N", title="Country")]
            ).properties(width=250,title=f'Compare {metric_title} averaged in {month} of {year} for selected countries')

#vaccination bar chart
vaccine_bar = alt.Chart(subset).mark_bar().transform_aggregate(
    most_recent_vax='argmax(total_vaccinations)/population',
    groupby=['Country','month','year']
).transform_calculate(
    latest_vaccinations_by_month='datum.most_recent_vax.total_vaccinations'
).encode(
    y=alt.Y(field='latest_vaccinations_by_month', type="quantitative"),
    x=alt.X(field="Country", type="nominal"),
    color='Country:N',
    tooltip=[
            alt.Tooltip(field='latest_vaccinations_by_month', type="quantitative", title=f'Total Vaccination by end of {month} of {year}'),
            alt.Tooltip("Country:N", title="Country")]
            ).properties(width=250,title=f'Compare total vaccinations by end of {month} of {year} for selected countries')


#create page layouts of charts
chart_trend=alt.hconcat(metric_chart_detail&metric_chart_global, r_chart_detail&r_chart_global).resolve_scale(color='independent')

chart_trend_worldmap=alt.vconcat(chart_trend, chart_worldmap).resolve_scale(color='independent')

chart_bar=alt.hconcat(bar,vaccine_bar)

chart_final = alt.vconcat(chart_trend_worldmap, chart_bar).resolve_scale(color='independent')

st.altair_chart(chart_final, use_container_width=True)








