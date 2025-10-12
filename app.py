import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ===========================
# CONFIGURACIÓN GENERAL
# ===========================
st.set_page_config(
    page_title="Dashboard de Riesgo de Readmisión",
    layout="wide",  # 👈 pantalla completa y horizontal
    page_icon="🏥"
)

st.title("🏥 Dashboard de Riesgo de Readmisión de Pacientes")

# ===========================
# CARGA DE DATOS
# ===========================
df = pd.read_csv("data_dashboard.csv", sep=",")

# ===========================
# SECCIÓN DE FILTROS
# ===========================
st.markdown("### 🔍 Filtros de Exploración")

# Crear columnas para mostrar filtros horizontalmente
col1, col2, col3, col4, col5, col6 = st.columns(6)

with col1:
    age = st.selectbox("Edad", options=["Todos"] + sorted(df['age'].unique().tolist()))

with col2:
    admission_type = st.selectbox("Tipo de admisión", options=["Todos"] + sorted(df['admission_type_id'].unique().tolist()))

with col3:
    insulin = st.selectbox("Tipo de insulina", options=["Todos"] + sorted(df['insulin'].unique().tolist()))

with col4:
    gender = st.selectbox("Género", options=["Todos"] + sorted(df['gender'].unique().tolist()))

with col5:
    race = st.selectbox("Raza", options=["Todos"] + sorted(df['race'].unique().tolist()))

with col6:
    hospital_range = st.slider(
        "Rango de días en hospital",
        min_value=int(df['time_in_hospital'].min()),
        max_value=int(df['time_in_hospital'].max()),
        value=(int(df['time_in_hospital'].min()), int(df['time_in_hospital'].max()))
    )

# ===========================
# FILTRADO DE DATOS
# ===========================
dff = df.copy()

if age != "Todos":
    dff = dff[dff['age'] == age]
if admission_type != "Todos":
    dff = dff[dff['admission_type_id'] == admission_type]
if insulin != "Todos":
    dff = dff[dff['insulin'] == insulin]
if gender != "Todos":
    dff = dff[dff['gender'] == gender]
if race != "Todos":
    dff = dff[dff['race'] == race]
if hospital_range:
    dff = dff[(dff['time_in_hospital'] >= hospital_range[0]) & (dff['time_in_hospital'] <= hospital_range[1])]

# ===========================
# VALIDACIÓN DE FILTROS
# ===========================
if dff.empty:
    st.warning("⚠️ No hay datos que coincidan con los filtros seleccionados.")
    st.stop()

# ===========================
# KPIs PRINCIPALES
# ===========================
tasa_readmit = round((dff['readmitted'] != 'NO').mean() * 100, 2)
prom_estancia = round(dff['time_in_hospital'].mean(), 2)
prom_meds = round(dff['num_medications'].mean(), 2)

st.markdown("### 📊 Indicadores Clave (KPIs)")

k1, k2, k3 = st.columns(3)
k1.metric("Tasa de Readmisión (%)", f"{tasa_readmit}%")
k2.metric("Promedio Estancia (días)", f"{prom_estancia}")
k3.metric("Promedio de Medicamentos", f"{prom_meds}")

# ===========================
# GRÁFICOS
# ===========================

st.markdown("### 📈 Visualizaciones")

# Crear filas de gráficos
c1, c2, c3 = st.columns(3)

# === Gauge Chart ===
with c1:
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=tasa_readmit,
        title={'text': "Tasa Readmisión (%)"},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': "red"},
            'steps': [
                {'range': [0, 20], 'color': "green"},
                {'range': [20, 40], 'color': "yellow"},
                {'range': [40, 100], 'color': "red"}]
        }
    ))
    st.plotly_chart(fig_gauge, use_container_width=True)

# === Scatter Chart ===
with c2:
    fig_scatter = px.scatter(
        dff, x='num_medications', y='time_in_hospital',
        color='readmitted', size='number_diagnoses',
        hover_data=['encounter_id', 'age', 'gender'],
        title="Medicaciones vs Tiempo en Hospital"
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

# === Bar Chart ===
with c3:
    df_bar = dff.groupby('admission_type_id')['readmitted'].apply(lambda x: (x != 'NO').mean() * 100).reset_index()
    fig_bar = px.bar(
        df_bar, x='admission_type_id', y='readmitted', color='admission_type_id',
        title="Tasa de Readmisión por Tipo de Admisión",
        labels={'readmitted': 'Tasa (%)'}
    )
    st.plotly_chart(fig_bar, use_container_width=True)

# === Heatmap ===
st.markdown("### 🧩 Mapa de calor de riesgo (Edad vs Diagnósticos)")

df_heat = dff.groupby(['age', 'number_diagnoses'])['readmitted'].apply(lambda x: (x != 'NO').mean()).reset_index()
fig_heat = px.density_heatmap(
    df_heat, x='age', y='number_diagnoses', z='readmitted',
    color_continuous_scale='Reds',
    title="Riesgo de Readmisión por Edad y Diagnósticos"
)
st.plotly_chart(fig_heat, use_container_width=True)

# === Tabla resumen ===
st.markdown("### 📋 Pacientes Filtrados")
st.dataframe(
    dff[["encounter_id", "age", "gender", "time_in_hospital", "num_medications", "readmitted"]],
    use_container_width=True
)


