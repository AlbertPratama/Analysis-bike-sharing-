import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency

sns.set(style='dark')

def create_daily_order(df):
    daily_order = df.resample(rule='D', on='dteday_x').agg({
        "instant": "nunique",
        "weekday_x": "sum"
    })
    daily_order = daily_order.reset_index()
    daily_order.rename(columns={
        "instant": "order_count",
        "weekday_x": "revenue"
    }, inplace=True)

    return daily_order

def create_sum_order_item(df):
    sum_order_item = df.groupby("weathersit_x").cnt_x.sum().sort_values(ascending=False).reset_index()
    return sum_order_item

def create_bytemp(df):
    by_temp = df.groupby(by="temp_group").instant.nunique().reset_index()
    by_temp.rename(columns={
        "instant": "customer_count"
    }, inplace=True)

    return by_temp

def create_byseason(df):
    byseason = df.groupby(by="season_x").instant.nunique().reset_index()
    byseason.rename(columns={
        "instant": "customer_count"
    }, inplace=True)
    byseason['season_X'] = pd.Categorical(byseason['season_x'], ['spring', 'summer', 'autumn', 'winter'])

    return byseason

def create_by_usage_time(df):
    by_usage_time = df.groupby(by="usage_time").instant.nunique().reset_index()
    by_usage_time.rename(columns={
        "instant": "customer_count"
    }, inplace=True)

    return by_usage_time

# Load data
all = pd.read_csv("day_hour_df.csv")

datetime_columns = ["mnth_x", "dteday_x"]
all.sort_values(by="dteday_x", inplace=True)
all.reset_index(drop=True, inplace=True)

for column in datetime_columns:
    all[column] = pd.to_datetime(all[column])

# Filter data
min_date = all["dteday_x"].min()
max_date = all["dteday_x"].max()

with st.sidebar:
    # start date & end date from input
    start_date, end_date = st.date_input(
        label='Rentang Waktu', min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

main_df = all[(all["dteday_x"] >= pd.to_datetime(start_date)) & (all["dteday_x"] <= pd.to_datetime(end_date))]

print(main_df.columns)

st.dataframe(main_df)

daily_order = create_daily_order(main_df)
sum_order = create_sum_order_item(main_df)
by_temp = create_bytemp(main_df)
by_season = create_byseason(main_df)
by_usage = create_by_usage_time(main_df)

st.header('Bike Sharing :sparkles:')
st.subheader('Daily Orders')

col1, col2 = st.columns(2)

with col1:
    total_order = daily_order.order_count.sum()
    st.metric("Total Order", value=total_order)

with col2:
    total_revenue = format_currency(daily_order.revenue.sum(), "AUD", locale='es_CO')
    st.metric("Total Revenue", value=total_revenue)

fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(
    daily_order['dteday_x'],
    daily_order['revenue'], 
    marker='o',
    linewidth=2,
    color="#90CAF9"
)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=20)

st.pyplot(fig)

# Performance
st.subheader("Best & Worst Performing")

fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(24, 6))

colors = ["#72BCD4", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

sns.barplot(x="cnt_x", y="weathersit_x", data=sum_order.head(5), palette=colors, ax=ax[0])  # Corrected column names
ax[0].set_ylabel(None)
ax[0].set_xlabel("Number of Order", fontsize=30)
ax[0].set_title("Best Performing Order", loc="center", fontsize=58)
ax[0].tick_params(axis="y", labelsize=35)
ax[0].tick_params(axis="x", labelsize=30)

sns.barplot(x="cnt_x", y="weathersit_x", data=sum_order.sort_values(by="cnt_x", ascending=True).head(5), palette=colors, ax=ax[1])  # Corrected column names
ax[1].set_ylabel(None)
ax[1].set_xlabel(None)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title("Worst Performing Order", loc="center", fontsize=50)
ax[1].tick_params(axis='y', labelsize=35)
ax[1].tick_params(axis='x', labelsize=30)

st.pyplot(fig)

# Customer Demographic
st.subheader("Customer Demographic")

col1, col2 = st.columns(2)

with col1:
    fig, ax = plt.subplots(figsize=(20, 10))

    sns.barplot(
        y="customer_count",
        x="temp_group",
        data=by_temp.sort_values(by="customer_count", ascending=False),
        palette=colors,
        ax=ax
    )
    ax.set_title("Number of Customer by Temp", loc="center", fontsize=50)
    ax.set_ylabel(None)
    ax.set_xlabel(None)
    ax.tick_params(axis='x', labelsize=35)
    ax.tick_params(axis='y', labelsize=30)
    st.pyplot(fig)

with col2:
    fig, ax = plt.subplots(figsize=(20, 10))

    colors = ["#D3D3D3", "#90CAF9", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

    sns.barplot(
        y="customer_count",
        x="season_x",
        data=by_season.sort_values(by="season_x", ascending=False),
        palette=colors,
        ax=ax
    )
    ax.set_title("Number of Customer by Season", loc="center", fontsize=50)
    ax.set_xlabel(None)
    ax.set_ylabel(None)
    ax.tick_params(axis='x', labelsize=35)
    ax.tick_params(axis='y', labelsize=30)
    st.pyplot(fig)

fig, ax = plt.subplots(figsize=(20, 10))
colors = ["#90CAF9", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
sns.barplot(
    x="customer_count",
    y="usage_time",
    data=by_usage.sort_values(by="customer_count"),
    palette=colors,
    ax=ax
)
ax.set_title("Number of Customer by Usage Time", loc="center")

st.pyplot(fig)
