import dash
from dash import html, dcc, callback_context
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
from datetime import datetime, timedelta
import time

# === IMPORT YOUR MODELS ===
from one_hour import run_signal_engine as run_one_hour
from one_hour_pro import run_signal_engine as run_one_hour_pro
from one_hour_pro_plus import run_signal_engine as run_one_hour_pro_plus
from one_hour_pro_max_ai import run_signal_engine as run_one_hour_pro_max

# === Initialize App ===
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CYBORG])  # Dark theme
app.title = "Forex Signal Dashboard"

# === Timer Function ===
def get_time_remaining():
    now = datetime.utcnow()
    next_hour = (now + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
    remaining = next_hour - now
    return str(remaining).split('.')[0], 3600 - remaining.seconds

# === Layout ===
app.layout = dbc.Container([
    html.H2("📊 Forex Signal Dashboard (1H, Pro, Pro+, Pro Max AI)", className="text-center mt-4"),

    html.Div(id='live-timer', className='text-center text-warning mb-3'),

    dcc.Interval(id="interval-component", interval=1*1000, n_intervals=0),  # 1 second interval

    dcc.Tabs(id="tabs", value='tab1', children=[
        dcc.Tab(label='📘 1 Hour', value='tab1'),
        dcc.Tab(label='📗 Pro', value='tab2'),
        dcc.Tab(label='📙 Pro+', value='tab3'),
        dcc.Tab(label='🚀 Pro Max AI', value='tab4'),
    ]),

    html.Div(id='tab-content')
], fluid=True)

# === Callbacks ===

@app.callback(
    Output('live-timer', 'children'),
    Input('interval-component', 'n_intervals')
)
def update_timer(n):
    countdown, elapsed = get_time_remaining()
    if elapsed <= 5:  # Auto refresh dashboards at start of hour
        return f"⏳ Time until next 1H candle: {countdown} – Refreshing dashboards..."
    return f"⏳ Time until next 1H candle: {countdown}"

@app.callback(
    Output('tab-content', 'children'),
    Input('tabs', 'value'),
    Input('interval-component', 'n_intervals')
)
def update_tab(tab, n):
    countdown, elapsed = get_time_remaining()
    refresh = elapsed <= 5

    if tab == 'tab1':
        df = run_one_hour() if refresh else pd.DataFrame()
        return generate_table(df, "1 Hour Model")
    elif tab == 'tab2':
        df = run_one_hour_pro() if refresh else pd.DataFrame()
        return generate_table(df, "1 Hour Pro Model")
    elif tab == 'tab3':
        df = run_one_hour_pro_plus() if refresh else pd.DataFrame()
        return generate_table(df, "1 Hour Pro+ Model")
    elif tab == 'tab4':
        df = run_one_hour_pro_max() if refresh else pd.DataFrame()
        return generate_table(df, "Pro Max AI Model")

# === Helper function to create data table ===
def generate_table(df, model_name):
    if df.empty:
        return dbc.Alert(f"No signals generated yet for {model_name}.", color="warning", className="m-3")
    else:
        return html.Div([
            html.H4(f"{model_name} Signals", className="text-info mt-3"),
            dbc.Table.from_dataframe(df, striped=True, bordered=True, hover=True, className="mt-2"),
        ])

# === Run the app ===
if __name__ == '__main__':
    app.run_server(debug=True)
