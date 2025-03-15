import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

sns.set(style='dark')

# Data Preparation
def load_data():
    day_df = pd.read_csv("data/day.csv")
    hour_df = pd.read_csv("data/hour.csv")
    
    # Convert datetime
    day_df['dteday'] = pd.to_datetime(day_df['dteday'])
    hour_df['dteday'] = pd.to_datetime(hour_df['dteday'])
    return day_df, hour_df

def create_hourly_analysis(df):
    df['hour'] = df['dteday'].dt.hour
    return df.groupby(['hour', 'workingday']).agg({'cnt': 'mean'}).reset_index()

def create_weather_corr(df):
    return df[['temp', 'hum', 'windspeed', 'cnt']].corr()

# Load data
day_df, hour_df = load_data()

# Streamlit Dashboard
st.title("Analisis Penyewaan Sepeda 🚲")

with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2972/2972185.png", width=100)
    
    # Fitur Interaktif 1: Filter Cuaca
    selected_weather = st.multiselect(
        'Pilih Kondisi Cuaca',
        options=[1, 2, 3, 4],
        default=[1, 2, 3, 4],
        format_func=lambda x: {1: 'Cerah', 2: 'Berawan', 3: 'Hujan Ringan', 4: 'Hujan Deras'}.get(x, 'Unknown')
    )
    
    # Fitur Interaktif 2: Pilih Faktor Cuaca
    weather_factor = st.selectbox(
        'Analisis Pengaruh Faktor Cuaca',
        options=['temp', 'hum', 'windspeed'],
        format_func=lambda x: {'temp': 'Suhu', 'hum': 'Kelembaban', 'windspeed': 'Kecepatan Angin'}[x]
    )

# Filter data
filtered_day_df = day_df[day_df['weathersit'].isin(selected_weather)]

# Visualisasi 1: Pengaruh Faktor Cuaca Terpilih
st.subheader("1. Hubungan Antara Faktor Cuaca dan Penyewaan")
fig, ax = plt.subplots(figsize=(10, 5))
sns.regplot(
    data=filtered_day_df,
    x=weather_factor,
    y='cnt',
    scatter_kws={'alpha':0.3},
    line_kws={'color':'red'}
)
plt.title(f"Pengaruh {weather_factor.capitalize()} Terhadap Penyewaan")
st.pyplot(fig)

# Visualisasi 2: Perbandingan Penyewaan Pagi Hari
st.subheader("2. Distribusi Penyewaan Pagi Hari (06.00-09.00)")
morning_hour_df = hour_df[(hour_df['hr'] >= 6) & (hour_df['hr'] <= 9)]
morning_stats = morning_hour_df.groupby('workingday').agg({'cnt':'mean'}).reset_index()

fig, ax = plt.subplots()
sns.barplot(
    data=morning_stats,
    x='workingday',
    y='cnt',
    palette='pastel',
    ax=ax
)
ax.set_xticklabels(['Akhir Pekan', 'Hari Kerja'])
ax.set_xlabel("")
ax.set_ylabel("Rata-rata Penyewaan")
st.pyplot(fig)

# Visualisasi 3: Analisis Cuaca Ekstrem
st.subheader("3. Efek Cuaca Ekstrem pada Penyewaan")
extreme_days = day_df[day_df['weathersit'] == 4]
normal_days = day_df[day_df['weathersit'].isin([1,2,3])]

fig, ax = plt.subplots()
sns.barplot(
    x=['Cuaca Ekstrem', 'Cuaca Normal'],
    y=[extreme_days['cnt'].mean(), normal_days['cnt'].mean()],
    palette=['#ff7f0e', '#1f77b4']
)
ax.set_ylabel("Rata-rata Penyewaan")
st.pyplot(fig)

# Visualisasi 4: Pola Harian Hari Kerja vs Akhir Pekan
st.subheader("4. Pola Penyewaan Per Jam")
hourly_df = create_hourly_analysis(hour_df)

fig, ax = plt.subplots(figsize=(12, 6))
sns.lineplot(
    data=hourly_df,
    x='hour',
    y='cnt',
    hue='workingday',
    palette='viridis',
    ax=ax
)
ax.set_xticks(range(0, 24))
ax.legend(title='Tipe Hari', labels=['Akhir Pekan', 'Hari Kerja'])
st.pyplot(fig)

# Visualisasi 5: Korelasi Faktor Cuaca
st.subheader("5. Matriks Korelasi Faktor Cuaca")
corr_matrix = create_weather_corr(filtered_day_df)

fig, ax = plt.subplots(figsize=(8, 6))
sns.heatmap(
    corr_matrix,
    annot=True,
    cmap='coolwarm',
    vmin=-1,
    vmax=1,
    ax=ax
)
st.pyplot(fig)

# Fitur Interaktif Tambahan
st.sidebar.header("Simulasi Strategi Promosi")
discount = st.sidebar.slider(
    "Besar Diskon (%) untuk Cuaca Ekstrem",
    0, 50, 20
)

# Simulasi efek diskon
base_rent = extreme_days['cnt'].mean()
simulated_rent = base_rent * (1 + discount/100)
st.sidebar.metric(
    "Perkiraan Peningkatan Penyewaan", 
    value=f"{simulated_rent:,.0f}",
    delta=f"{discount}% Diskon"
)