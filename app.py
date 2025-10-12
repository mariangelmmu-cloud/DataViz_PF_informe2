import dash
from dash import html, dcc, dash_table, Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go



df = pd.read_csv("data_dashboard.csv", sep=",")

# ===========================
# Inicializar la app
# ===========================
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])
app.title = "Dashboard de Riesgo de Readmisión"
server = app.server  # necesario para Render

# ===========================
# Layout
# ===========================
app.layout = dbc.Container(fluid=True, children=[

    # 🔹 Fila 1: Filtros + KPIs
    dbc.Row([
        # Filtros
        dbc.Col([
            html.H4("Filtros", className="text-primary mb-2"),
            dcc.Dropdown(
                id='filter_age',
                options=[{'label': a, 'value': a} for a in sorted(df['age'].unique())],
                placeholder="Selecciona edad",
                multi=False
            ),
            dcc.Dropdown(
                id='filter_admission',
                options=[{'label': a, 'value': a} for a in sorted(df['admission_type_id'].unique())],
                placeholder="Tipo de admisión",
                multi=False
            ),
            dcc.Dropdown(
                id='filter_insulin',
                options=[{'label': a, 'value': a} for a in sorted(df['insulin'].unique())],
                placeholder="Tipo de insulina",
                multi=False
            ),
            dcc.Dropdown(
                id='filter_gender',
                options=[{'label': g, 'value': g} for g in sorted(df['gender'].unique())],
                placeholder="Género",
                multi=False
            ),
            dcc.Dropdown(
                id='filter_race',
                options=[{'label': r, 'value': r} for r in sorted(df['race'].unique())],
                placeholder="Raza",
                multi=False
            ),
            html.Label("Rango de días en hospital:"),
            dcc.RangeSlider(
                id='slider_hospital',
                min=df['time_in_hospital'].min(),
                max=df['time_in_hospital'].max(),
                step=1,
                marks={i: str(i) for i in range(df['time_in_hospital'].min(), df['time_in_hospital'].max() + 1)},
                value=[df['time_in_hospital'].min(), df['time_in_hospital'].max()]
            )
        ], width=4),

        # KPIs
        dbc.Col([
            html.H4("Indicadores Clave", className="text-primary mb-2"),
            dbc.Row([
                dbc.Col(dbc.Card([html.H6("Tasa de Readmisión"), html.H4(id='kpi_readmit')], color='danger', inverse=True), width=4),
                dbc.Col(dbc.Card([html.H6("Promedio Estancia"), html.H4(id='kpi_stay')], color='primary', inverse=True), width=4),
                dbc.Col(dbc.Card([html.H6("Medicación Promedio"), html.H4(id='kpi_med')], color='success', inverse=True), width=4),
            ])
        ], width=8)
    ], className="mb-3"),

    # 🔹 Fila 2: Gráficos principales
    dbc.Row([
        dbc.Col(dcc.Graph(id='gauge_chart', style={'height': '40vh'}), width=4),
        dbc.Col(dcc.Graph(id='scatter_chart', style={'height': '40vh'}), width=4),
        dbc.Col(dcc.Graph(id='bar_chart', style={'height': '40vh'}), width=4),
    ], className="mb-3"),

    # 🔹 Fila 3: Heatmap + Tabla
    dbc.Row([
        dbc.Col(dcc.Graph(id='heatmap_chart', style={'height': '35vh'}), width=6),
        dbc.Col(dash_table.DataTable(
            id='patient_table',
            columns=[{"name": i, "id": i} for i in ["encounter_id", "age", "gender", "time_in_hospital", "num_medications", "readmitted"]],
            style_table={'height': '35vh', 'overflowY': 'auto'},
            style_cell={'fontSize': 12, 'textAlign': 'center'},
            page_size=8
        ), width=6),
    ])
], style={'height': '100vh', 'overflow': 'hidden', 'padding': '10px'})


# ===========================
# Callbacks
# ===========================
@app.callback(
    [
        Output('kpi_readmit', 'children'),
        Output('kpi_stay', 'children'),
        Output('kpi_med', 'children'),
        Output('gauge_chart', 'figure'),
        Output('scatter_chart', 'figure'),
        Output('bar_chart', 'figure'),
        Output('heatmap_chart', 'figure'),
        Output('patient_table', 'data')
    ],
    [
        Input('filter_age', 'value'),
        Input('filter_admission', 'value'),
        Input('filter_insulin', 'value'),
        Input('filter_gender', 'value'),
        Input('filter_race', 'value'),
        Input('slider_hospital', 'value')
    ]
)
def update_dashboard(age, admission_type, insulin, gender, race, hospital_range):
    dff = df.copy()

    # Aplicar filtros
    if age:
        dff = dff[dff['age'] == age]
    if admission_type:
        dff = dff[dff['admission_type_id'] == admission_type]
    if insulin:
        dff = dff[dff['insulin'] == insulin]
    if gender:
        dff = dff[dff['gender'] == gender]
    if race:
        dff = dff[dff['race'] == race]
    if hospital_range:
        dff = dff[(dff['time_in_hospital'] >= hospital_range[0]) & (dff['time_in_hospital'] <= hospital_range[1])]

    # Evitar división por cero
    if dff.empty:
        return "N/A", "N/A", "N/A", go.Figure(), go.Figure(), go.Figure(), go.Figure(), []

    # === KPIs ===
    tasa_readmit = round((dff['readmitted'] != 'NO').mean() * 100, 2)
    prom_estancia = round(dff['time_in_hospital'].mean(), 2)
    prom_meds = round(dff['num_medications'].mean(), 2)

    # === Gauge chart ===
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=tasa_readmit,
        title={'text': "Tasa Readmisión (%)"},
        gauge={'axis': {'range': [0, 100]},
               'bar': {'color': "red"},
               'steps': [{'range': [0, 20], 'color': "green"},
                         {'range': [20, 40], 'color': "yellow"},
                         {'range': [40, 100], 'color': "red"}]}
    ))
    fig_gauge.update_layout(margin=dict(l=20, r=20, t=40, b=20))

    # === Scatter chart ===
    fig_scatter = px.scatter(
        dff, x='num_medications', y='time_in_hospital',
        color='readmitted', size='number_diagnoses',
        hover_data=['encounter_id', 'age', 'gender'],
        title="Medicaciones vs Tiempo de Hospitalización"
    )

    # === Bar chart ===
    df_bar = dff.groupby('admission_type_id')['readmitted'].apply(lambda x: (x != 'NO').mean() * 100).reset_index()
    fig_bar = px.bar(df_bar, x='admission_type_id', y='readmitted', color='admission_type_id',
                     title="Tasa de Readmisión por Tipo de Admisión")
    fig_bar.update_yaxes(title="Tasa (%)")

    # === Heatmap ===
    df_heat = dff.groupby(['age', 'number_diagnoses'])['readmitted'].apply(lambda x: (x != 'NO').mean()).reset_index()
    fig_heat = px.density_heatmap(df_heat, x='age', y='number_diagnoses', z='readmitted',
                                  color_continuous_scale='Reds', title="Riesgo: Edad vs Diagnósticos")
    fig_heat.update_coloraxes(colorbar_title="Tasa Readmisión")

    # === Tabla resumen ===
    table_data = dff[["encounter_id", "age", "gender", "time_in_hospital", "num_medications", "readmitted"]].to_dict('records')

    return f"{tasa_readmit}%", f"{prom_estancia}", f"{prom_meds}", fig_gauge, fig_scatter, fig_bar, fig_heat, table_data


# ===========================
# Run
# ===========================
if __name__ == "__main__":
    app.run_server(debug=True, port=8050)
