import pandas as pd
import plotly.graph_objs as go
from plotly.subplots import make_subplots

# Load data, skip any header rows that may have been written by mistake
oil = pd.read_csv("oilindia_10y_daily.csv", index_col=0)  # <-- Change filename here
wti = pd.read_csv("wti_10y_daily.csv", index_col=0)

# Remove any rows where the index is not a date (e.g., accidental header rows)
oil = oil[~oil.index.astype(str).str.contains("Ticker|ticker|date|Date", case=False, na=False)]
wti = wti[~wti.index.astype(str).str.contains("Ticker|ticker|date|Date", case=False, na=False)]

# Ensure index is DatetimeIndex with explicit format
date_format = "%Y-%m-%d"
oil.index = pd.to_datetime(oil.index, format=date_format, errors='coerce')
wti.index = pd.to_datetime(wti.index, format=date_format, errors='coerce')

# Drop rows where index could not be converted to datetime
oil = oil[~oil.index.isna()]
wti = wti[~wti.index.isna()]

# Ensure columns are correct and numeric
for df in [oil, wti]:
    for col in ['Open', 'High', 'Low', 'Close', 'Volume']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    df.dropna(subset=['Open', 'High', 'Low', 'Close'], inplace=True)
    if 'Volume' in df.columns:
        df['Volume'] = df['Volume'].fillna(0)

# Select a recent window for clarity (e.g., last 180 days)
oil_recent = oil.tail(180)
wti_recent = wti.tail(180)

# Align both dataframes on the same dates for plotting
common_idx = oil_recent.index.intersection(wti_recent.index)
oil_recent = oil_recent.loc[common_idx]
wti_recent = wti_recent.loc[common_idx]

# Create interactive candlestick subplots with Plotly
fig = make_subplots(
    rows=2, cols=1, shared_xaxes=True,
    vertical_spacing=0.05,
    subplot_titles=("OIL INDIA NSE Candlestick (INR)", "WTI Crude Oil Futures Candlestick (USD)")
)

# OIL INDIA Candlestick
fig.add_trace(
    go.Candlestick(
        x=oil_recent.index,
        open=oil_recent['Open'],
        high=oil_recent['High'],
        low=oil_recent['Low'],
        close=oil_recent['Close'],
        name='OIL INDIA',
        increasing_line_color='green',
        decreasing_line_color='red',
        hovertext=[
            f"<b>Date</b>: {d.strftime('%Y-%m-%d')}<br>"
            f"<b>Open</b>: {o}<br>"
            f"<b>High</b>: {h}<br>"
            f"<b>Low</b>: {l}<br>"
            f"<b>Close</b>: {c}"
            for d, o, h, l, c in zip(
                oil_recent.index,
                oil_recent['Open'],
                oil_recent['High'],
                oil_recent['Low'],
                oil_recent['Close']
            )
        ],
        hoverinfo="text"
    ),
    row=1, col=1
)

# WTI Candlestick
fig.add_trace(
    go.Candlestick(
        x=wti_recent.index,
        open=wti_recent['Open'],
        high=wti_recent['High'],
        low=wti_recent['Low'],
        close=wti_recent['Close'],
        name='WTI',
        increasing_line_color='blue',
        decreasing_line_color='orange',
        hovertext=[
            f"<b>Date</b>: {d.strftime('%Y-%m-%d')}<br>"
            f"<b>Open</b>: {o}<br>"
            f"<b>High</b>: {h}<br>"
            f"<b>Low</b>: {l}<br>"
            f"<b>Close</b>: {c}"
            for d, o, h, l, c in zip(
                wti_recent.index,
                wti_recent['Open'],
                wti_recent['High'],
                wti_recent['Low'],
                wti_recent['Close']
            )
        ],
        hoverinfo="text"
    ),
    row=2, col=1
)

# Fancy design: dark theme, grid, vanishing hover box, and range slider
fig.update_layout(
    template='plotly_dark',
    hovermode='x unified',
    xaxis_rangeslider_visible=False,
    xaxis2_rangeslider_visible=True,
    xaxis2_rangeslider_thickness=0.05,
    height=800,
    margin=dict(t=60, b=40, l=40, r=40),
    plot_bgcolor='#222',
    paper_bgcolor='#222',
    font=dict(family="Arial", size=13, color="#fff"),
    title_text="ONGC vs WTI Crude Oil - Interactive Candlestick Comparison"
)

fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#444')
fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#444')

fig.show()

