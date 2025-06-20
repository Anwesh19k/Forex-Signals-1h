import dash
from dash import dcc, html, Output, Input
import pandas as pd
from datetime import datetime, timedelta
import dash_bootstrap_components as dbc

# === Your signal engine imports ===
from one_hour import run_signal_engine as run_one_hour
from one_hour_pro import run_signal_engine as run_one_hour_pro
from one_hour_pro_plus import run_signal_engine as run_one_hour_pro_plus
from one_hour_pro_max_ai import run_signal_engine as run_one_hour_pro_max

# === Initialize the Dash app ===
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])
app.title = "Forex Signal Dashboard"
server = app.server  # for Railway deployment

# === Layout ===
app.layout = dbc.Container([
    html.H2("📊 Forex Signal Dashboard (1H, Pro, Pro+, Pro Max AI)", className="text-center my-3"),

    html.H4(id="live-timer", className="text-center text-warning mb-4"),

    dcc.Interval(id="timer-interval", interval=1000, n_intervals=0),

    dbc.Tabs([
        dbc.Tab(label="📘 1 Hour", tab_id="tab1"),
        dbc.Tab(label="📗 Pro", tab_id="tab2"),
        dbc.Tab(label="📙 Pro+", tab_id="tab3"),
        dbc.Tab(label="🚀 Pro Max AI", tab_id="tab4"),
    ], id="tabs", active_tab="tab1", className="mb-4"),

    html.Div(id="tab-content")
], fluid=True)


# === Timer Update Function ===
@app.callback(
    Output("live-timer", "children"),
    Input("timer-interval", "n_intervals")
)
def update_countdown(n):
    now = datetime.utcnow()
    next_hour = (now + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
    remaining = next_hour - now
    seconds = remaining.total_seconds()
    minutes, secs = divmod(int(seconds), 60)
    return f"🕒 Time Left for Next 1H Candle: {minutes:02}:{secs:02}"


# === Dashboard Auto-Refresh at HH:00 ===
@app.callback(
    Output("tab-content", "children"),
    Input("tabs", "active_tab"),
    Input("timer-interval", "n_intervals")
)
def render_tab(tab, n):
    # Auto-refresh every HH:00:05
    now = datetime.utcnow()
    auto_refresh = (now.minute == 0 and now.second <= 5)

    if tab == "tab1":
        df = run_one_hour() if auto_refresh else pd.DataFrame()
        return generate_table(df, "📘 1 Hour Model (Standard)")

    elif tab == "tab2":
        df = run_one_hour_pro() if auto_refresh else pd.DataFrame()
        return generate_table(df, "📗 1 Hour Model (Pro)")

    elif tab == "tab3":
        df = run_one_hour_pro_plus() if auto_refresh else pd.DataFrame()
        return generate_table(df, "📙 1 Hour Model (Pro+)")

    elif tab == "tab4":
        df = run_one_hour_pro_max() if auto_refresh else pd.DataFrame()
        return generate_table(df, "🚀 1 Hour Model (Pro Max AI)")

    return "No tab selected."


# === Helper to Render Table ===
def generate_table(df, header):
    if df.empty:
        return html.Div([
            html.H5(header, className="text-info"),
            html.Div("⚠️ No signals generated or model skipped.", className="text-warning")
        ])
    else:
        return html.Div([
            html.H5(header, className="text-success"),
            dbc.Table.from_dataframe(df, striped=True, bordered=True, hover=True, responsive=True, className="mt-2")
        ])


# === Run App ===
if __name__ == '__main__':
    app.run_server(debug=True)


# === Run the app ===
if __name__ == '__main__':
    app.run_server(debug=True)
