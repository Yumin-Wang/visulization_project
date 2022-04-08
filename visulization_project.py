import pandas as pd
import numpy as np
import datetime as dt
import altair as alt
import streamlit as st

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
    covid['total_cases_per_million']= covid['total_deaths_per_million'].fillna(method='bfill').fillna(method='ffill')
    covid['new_cases_per_million']= covid['new_cases_per_million'].fillna(method='bfill').fillna(method='ffill')
    covid['total_deaths_per_million']= covid['total_deaths_per_million'].fillna(method='bfill').fillna(method='ffill')
    covid['reproduction_rate']= covid['reproduction_rate'].fillna(method='bfill').fillna(method='ffill')
    country_df['Country'] = country_df['Country'].replace(['United States of America','United Kingdom of Great Britain and Northern Ireland'],['United States','United Kingdom'])
    covid.rename(columns = {'location' : 'Country'}, inplace = True)
    covid = covid.merge(country_df,how='left',on='Country')
    covid.dropna(inplace=True)
    return covid

df = load_data()

st.write("## Covid related graph")

year=st.radio(label='Year', options=df['year'].unique(), index=0)
subset = df[df["year"] == year]

month=st.selectbox(label='Month', options=list(subset['month'].unique()), index=0)
subset = subset[subset["month"] == month]

continent=st.selectbox(label='Continent', options=list(subset['continent'].unique()), index=0)
subset = subset[subset["continent"] == continent]

countries=st.multiselect(label='Countries', options=list(subset['Country'].unique()))
subset = subset[subset["Country"].isin(countries)]
















