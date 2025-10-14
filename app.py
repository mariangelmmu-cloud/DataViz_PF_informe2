import matplotlib.pyplot as plt
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from streamlit_option_menu import option_menu
import seaborn as sns


# ===========================
# CONFIGURACIÓN GENERAL
# ===========================
st.set_page_config(
    page_title="Dashboard de Riesgo de Readmisión",
    layout="wide",
    page_icon="🏥"
)

with st.sidebar:
    page = option_menu("Menú", ["Inicio", "Análisis", "Dashboard"],
        icons=["house", "geo-alt", "bar-chart"], menu_icon="cast", default_index=0)

# ===========================
# TÍTULO
# ===========================
st.title("🏥 Dashboard de Riesgo de Readmisión de Pacientes")

# ===========================
# CARGA DE DATOS
# ===========================
df = pd.read_csv("data_nombres.csv", sep=",")

if page == "Inicio":
    st.title("Contexto de la base de datos")

    st.markdown("""
        ## **Origen y tamaño del dataset**
        Los datos provienen del UCI Machine Learning Repository, en el conjunto “Diabetes 130-US hospitals for years 1999–2008 Data Set”, recopilado de registros hospitalarios electrónicos de 130 hospitales y redes médicas en EE.UU.
                [UCI Machine Learning Repository - Diabetes 130-US hospitals for years 1999–2008](https://archive.ics.uci.edu/dataset/296/diabetes+130-us+hospitals+for+years+1999-2008)

        Este dataset cuenta con un total de 50 variables y 101766 registros.

    """
    )


    st.markdown(
        """
        ## **Descripción de Variables**

A continuación se describen las variables presentes en el dataset `diabetic_data.csv`, organizadas por categorías y con sus respectivas unidades o escalas de medición.

---

## 🔐 Variables de Identificación

| Variable       | Tipo       | Unidad / Escala | Descripción |
|----------------|------------|------------------|-------------|
| `encounter_id` | Numérica   | — | Identificador único del encuentro hospitalario (visita). |
| `patient_nbr`  | Numérica   | — | Identificador único del paciente. |

---

## 👤 Datos Demográficos y de Ingreso

| Variable               | Tipo        | Unidad / Escala | Descripción |
|------------------------|-------------|------------------|-------------|
| `race`                 | Categórica  | — | Raza del paciente. Valores: Caucasian, Asian, African American, Hispanic, Other. |
| `gender`               | Categórica  | — | Género del paciente. Valores: male, female, unknown/invalid. |
| `age`                  | Categórica  | Años (rangos de 10 años) | Edad agrupada en intervalos de 10 años (ej. [50-60)). |
| `weight`               | Categórica  | Libras (lbs) | Peso del paciente (en libras). Muchos valores faltantes. |
| `admission_type_id`    | Categórica (codificada) | — | Tipo de admisión (1=Emergency, 2=Urgent, 3=Elective, etc.). |
| `discharge_disposition_id` | Categórica (codificada) | — | Disposición al alta. Indica el destino del paciente al ser dado de alta. |
| `admission_source_id`  | Categórica (codificada) | — | Fuente de admisión (referencia médica, urgencias, etc.). |
| `time_in_hospital`     | Numérica    | Días | Días de estancia en el hospital. |

---

## 🔬 Pruebas y Procedimientos

| Variable             | Tipo     | Unidad / Escala | Descripción |
|----------------------|----------|------------------|-------------|
| `num_lab_procedures` | Numérica | Conteo | Número de pruebas de laboratorio realizadas. |
| `num_procedures`     | Numérica | Conteo | Número de procedimientos distintos realizados (excluye laboratorios). |
| `num_medications`    | Numérica | Conteo | Número de medicamentos diferentes administrados. |
| `number_outpatient`  | Numérica | Conteo | Número de visitas ambulatorias previas. |
| `number_emergency`   | Numérica | Conteo | Número de visitas a urgencias previas. |
| `number_inpatient`   | Numérica | Conteo | Número de ingresos hospitalarios previos. |
| `number_diagnoses`   | Numérica | Conteo | Número de diagnósticos registrados. |

---

## 🏥 Diagnósticos Principales

| Variable | Tipo     | Unidad / Escala | Descripción |
|----------|----------|------------------|-------------|
| `diag_1` | Categórica | Código ICD9 | Diagnóstico principal (código ICD9, 3 dígitos). |
| `diag_2` | Categórica | Código ICD9 | Diagnóstico secundario. |
| `diag_3` | Categórica | Código ICD9 | Diagnóstico adicional. |

---

## 💉 Resultados de Laboratorio

| Variable       | Tipo       | Unidad / Escala | Descripción |
|----------------|------------|------------------|-------------|
| `max_glu_serum`| Categórica | mg/dL (implícita) | Resultado máximo de glucosa en suero. Valores: >200, >300, normal, none. |
| `A1Cresult`    | Categórica | % (hemoglobina glicosilada) | Resultado de hemoglobina A1C. Valores: >8, >7, normal, none. |

---

## 💊 Medicamentos Administrados

Cada una de las siguientes variables indica si el medicamento fue administrado y si hubo cambio de dosis.  
**Valores posibles:** `up`, `down`, `steady`, `no`.

**Variables:**

`metformin`, `repaglinide`, `nateglinide`, `chlorpropamide`, `glimepiride`, `acetohexamide`, `glipizide`, `glyburide`, `tolbutamide`, `pioglitazone`, `rosiglitazone`, `acarbose`, `miglitol`, `troglitazone`, `tolazamide`, `examide`, `citoglipton`, `insulin`, `glyburide-metformin`, `glipizide-metformin`, `glimepiride-pioglitazone`, `metformin-rosiglitazone`, `metformin-pioglitazone`.

---

## ⚙️ Control del Tratamiento

| Variable      | Tipo       | Unidad / Escala | Descripción |
|---------------|------------|------------------|-------------|
| `change`      | Categórica | — | Indica si hubo algún cambio en los medicamentos para la diabetes durante la estancia (`change`, `no change`). |
| `diabetesMed` | Categórica | — | Indica si se prescribió algún medicamento para la diabetes (`yes`, `no`). |

---

## 🎯 Variable Objetivo

| Variable     | Tipo       | Unidad / Escala | Descripción |
|--------------|------------|------------------|-------------|
| `readmitted` | Categórica | Días desde el alta | Indica si el paciente fue readmitido y cuándo. Valores: `<30` (antes de 30 días), `>30` (después de 30 días), `No` (sin reingreso). |

---

### 📌 **Notas adicionales**

- Los diagnósticos (`diag_1`, `diag_2`, `diag_3`) usan **códigos ICD-9**, donde, por ejemplo:  
  - `250.xx` → Diabetes mellitus.  
  - `401.xx` → Hipertensión esencial.  
  - `414.xx` → Enfermedad cardíaca isquémica.  
- Las variables `age` y `weight` se presentan en **intervalos discretos** para proteger la privacidad del paciente.  
- Los valores `?` representan **datos faltantes o no registrados**.  
- Los resultados de laboratorio (`max_glu_serum`, `A1Cresult`) son **rangos categóricos** basados en valores clínicos.
---

        """
    )

elif page == "Análisis":
    st.title("Análisis Exploratorio Interactivo de Datos")

    df = pd.read_csv("data_nombres.csv", sep=",")

    # Detección automática de variables numéricas y categóricas
    num_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
    cat_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()

    # =====================================================
    # SECCIÓN 1: ANÁLISIS UNIVARIADO
    # =====================================================
    st.header("Análisis Univariado")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Variables Numéricas")
        var_num = st.selectbox("Selecciona una variable numérica:", num_cols, key="uni_num")
        if var_num:
            fig, ax = plt.subplots(figsize=(6, 4))
            sns.histplot(df[var_num].dropna(), kde=True, color="skyblue", ax=ax)
            ax.set_title(f"Distribución de {var_num}")
            st.pyplot(fig)

            st.write("**Estadísticas descriptivas:**")
            st.write(df[var_num].describe().round(2))

    with col2:
        st.subheader("Variables Categóricas")
        var_cat = st.selectbox("Selecciona una variable categórica:", cat_cols, key="uni_cat")
        if var_cat:
            fig, ax = plt.subplots(figsize=(6, 4))
            sns.countplot(data=df, x=var_cat, palette="Set2", ax=ax)
            ax.set_title(f"Frecuencias de {var_cat}")
            plt.xticks(rotation=25)
            st.pyplot(fig)

            st.write("**Conteo de categorías:**")
            st.write(df[var_cat].value_counts())

    st.markdown("---")

    # =====================================================
    # SECCIÓN 2: ANÁLISIS BIVARIADO
    # =====================================================
    st.header("Análisis Bivariado")

    # -------------------------------
    # Numérica vs Categórica
    # -------------------------------
    st.subheader("Numérica vs Categórica")
    col1, col2 = st.columns(2)

    with col1:
        x_cat = st.selectbox("Variable categórica (X):", cat_cols, key="biv_cat")
    with col2:
        y_num = st.selectbox(
            "Variable numérica (Y):", 
            [col for col in num_cols if col != x_cat], 
            key="biv_num"
        )

    if x_cat and y_num:
        fig, ax = plt.subplots(figsize=(7, 4))
        sns.boxplot(data=df, x=x_cat, y=y_num, palette="Set3", ax=ax)
        ax.set_title(f"{y_num} según {x_cat}")
        plt.xticks(rotation=25)
        st.pyplot(fig)

    st.markdown("---")

    # -------------------------------
    # Categórica vs Categórica
    # -------------------------------
    st.subheader("Categórica vs Categórica")
    col1, col2 = st.columns(2)

    with col1:
        cat_x = st.selectbox("Variable categórica (X):", cat_cols, key="biv_cat_x")
    with col2:
        cat_hue = st.selectbox(
            "Variable categórica (agrupación):", 
            [col for col in cat_cols if col != cat_x], 
            key="biv_cat_hue"
        )

    if cat_x and cat_hue:
        fig, ax = plt.subplots(figsize=(7, 4))
        sns.countplot(data=df, x=cat_x, hue=cat_hue, palette="Set2", ax=ax)
        ax.set_title(f"Distribución de {cat_x} por {cat_hue}")
        plt.xticks(rotation=25)
        # Colocar la leyenda fuera del gráfico
        ax.legend(title=cat_hue, bbox_to_anchor=(1.05, 1), loc='upper left')
        st.pyplot(fig)

        st.write("**Tabla de contingencia:**")
        st.write(pd.crosstab(df[cat_x], df[cat_hue]))

    st.markdown("---")

    # -------------------------------
    # Numérica vs Numérica
    # -------------------------------
    st.subheader("Numérica vs Numérica")
    col1, col2, col3 = st.columns(3)

    with col1:
        num_x = st.selectbox("Variable numérica (X):", num_cols, key="biv_num_x")
    with col2:
        num_y = st.selectbox(
            "Variable numérica (Y):", 
            [col for col in num_cols if col != num_x], 
            key="biv_num_y"
        )
    with col3:
        hue_opt = st.selectbox(
            "Color por variable categórica (opcional):", 
            [None] + cat_cols, 
            key="biv_hue"
        )

    if num_x and num_y:
        fig, ax = plt.subplots(figsize=(7, 4))
        sns.scatterplot(data=df, x=num_x, y=num_y, hue=hue_opt, palette="coolwarm", ax=ax)
        ax.set_title(f"Relación entre {num_x} y {num_y}")
        st.pyplot(fig)

        st.write("**Correlación de Spearman:**")
        corr = df[[num_x, num_y]].corr(method='spearman').iloc[0, 1]
        st.metric(label="Coeficiente de correlación", value=round(corr, 3))

    st.markdown("---")

    # =====================================================
    # SECCIÓN 3: ANÁLISIS MULTIVARIADO
    # =====================================================
    st.header("Análisis Multivariado")

    st.subheader("Mapa de Calor de Correlaciones (variables numéricas)")

    if len(num_cols) >= 2:
        fig, ax = plt.subplots(figsize=(8, 6))
        corr_matrix = df[num_cols].corr(method='spearman')
        sns.heatmap(corr_matrix, annot=True, cmap="coolwarm", fmt=".2f", ax=ax)
        ax.set_title("Matriz de correlaciones (Spearman)")
        st.pyplot(fig)
    else:
        st.warning("⚠️ Se necesitan al menos dos variables numéricas para el mapa de calor.")

    st.markdown("---")


else: 
    df = pd.read_csv("data_nombres.csv", sep=",")
    # ===========================
    # AGRUPACIÓN DE EDADES
    # ===========================
    try:
        df['age'] = df['age'].astype(float)
    except:
        pass

    bins = [0, 20, 40, 60, 80, 120]
    labels = ['0-20', '21-40', '41-60', '61-80', '81+']

    # ===========================
    # SECCIÓN DE FILTROS
    # ===========================
    st.markdown("###### Filtros de Exploración")

    col1, col2, col3, col4, col5, col6 = st.columns(6)

    with col2:
        age = st.selectbox("Grupo de Edad", options=["Todos"] +  sorted(df['age'].unique().tolist()))
    with col3:
        admission_type = st.selectbox("Tipo de admisión", options=["Todos"] + sorted(df['admission_type'].unique().tolist()))
    with col4:
        insulin = st.selectbox("Tipo de insulina", options=["Todos"] + sorted(df['insulin'].unique().tolist()))
    with col5:
        gender = st.selectbox("Género", options=["Todos"] + sorted(df['gender'].unique().tolist()))
    with col6:
        hospital_range = st.slider(
            "Rango de días en hospital",
            min_value=int(df['time_in_hospital'].min()),
            max_value=int(df['time_in_hospital'].max()),
            value=(int(df['time_in_hospital'].min()), int(df['time_in_hospital'].max()))
        )
    with col1:
        readmit_filter = st.selectbox(
            "Estado de Readmisión",
            options=["Todos"] + sorted(df['readmitted'].unique().tolist())
        )

    # ===========================
    # FILTRADO DE DATOS
    # ===========================
    dff = df.copy()

    if age != "Todos":
        dff = dff[dff['age_group'] == age]
    if admission_type != "Todos":
        dff = dff[dff['admission_type'] == admission_type]
    if insulin != "Todos":
        dff = dff[dff['insulin'] == insulin]
    if gender != "Todos":
        dff = dff[dff['gender'] == gender]
    if readmit_filter != "Todos":
        dff = dff[dff['readmitted'] == readmit_filter]
    if hospital_range:
        dff = dff[
            (dff['time_in_hospital'] >= hospital_range[0]) &
            (dff['time_in_hospital'] <= hospital_range[1])
        ]

    if dff.empty:
        st.warning("⚠️ No hay datos que coincidan con los filtros seleccionados.")
        st.stop()

    # ===========================
    # KPIs PRINCIPALES
    # ===========================
    tasa_readmit = round((dff['readmitted'] != 'NO').mean() * 100, 2)
    prom_estancia = round(dff['time_in_hospital'].mean(), 2)
    prom_meds = round(dff['num_medications'].mean(), 2)
    cant_personas = len(dff)

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Cantidad de Pacientes", f"{cant_personas:,}")
    k2.metric("Tasa de Readmisión (%)", f"{tasa_readmit}%")
    k3.metric("Promedio Estancia (días)", f"{prom_estancia}")
    k4.metric("Promedio de Medicamentos", f"{prom_meds}")

    # ===========================
    # GRÁFICOS
    # ===========================

    col1, col2 = st.columns([1, 2])

    with col1:
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=tasa_readmit,
            title={'text': "Tasa Readmisión (%)"},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': "royalblue"},
                'steps': [
                    {'range': [0, 20], 'color': "#b8e994"},
                    {'range': [20, 40], 'color': "#f6e58d"},
                    {'range': [40, 100], 'color': "#ff7979"}
                ]
            }
        ))
        fig_gauge.update_layout(height=350, margin=dict(l=10, r=10, t=40, b=10))
        st.plotly_chart(fig_gauge, use_container_width=True)

    with col2:
        fig_scatter = px.scatter(
            dff, x='num_medications', y='time_in_hospital',
            color='readmitted', size='number_diagnoses',
            hover_data=['encounter_id', 'age', 'gender'],
            title="Medicaciones vs Tiempo en Hospital"
        )
        fig_scatter.update_layout(height=400)
        st.plotly_chart(fig_scatter, use_container_width=True)

    col3, col4 = st.columns(2)

    with col3:
        df_bar = dff.groupby('admission_type')['readmitted'].apply(lambda x: (x != 'NO').mean() * 100).reset_index()
        fig_bar = px.bar(
            df_bar, x='admission_type', y='readmitted', color='admission_type',
            title="Tasa de Readmisión por Tipo de Admisión",
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig_bar.update_layout(height=400)
        st.plotly_chart(fig_bar, use_container_width=True)

    with col4:
        df_heat = dff.groupby(['age', 'number_diagnoses'])['readmitted'].apply(lambda x: (x != 'NO').mean()).reset_index()
        fig_heat = px.density_heatmap(
            df_heat, x='age', y='number_diagnoses', z='readmitted',
            color_continuous_scale='Blues',
            title="Riesgo de Readmisión: Edad vs Diagnósticos"
        )
        fig_heat.update_layout(height=400)
        st.plotly_chart(fig_heat, use_container_width=True)

    # === Tabla resumen ===
    st.markdown("### Tabla de Pacientes Filtrados")
    st.dataframe(
        dff[["encounter_id", "age", "gender", "time_in_hospital", "num_medications", "readmitted"]],
        use_container_width=True
    )


