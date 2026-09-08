import streamlit as st
import pandas as pd
import plotly.express as px
import os
import re
import time
st.set_page_config(
    page_title="Cryptocurrency Price Tracker",
    page_icon="💰",
    layout="wide"
)

st.title("💰 Cryptocurrency Price Tracker")
st.write("Real-time cryptocurrency data collected using Selenium")
col_refresh, col_space = st.columns([1, 5])

with col_refresh:
    if st.button("🔄 Refresh Data"):
        st.cache_data.clear()
        st.rerun()

file_name = "crypto_prices.csv"

if not os.path.exists(file_name):
    st.error("❌ crypto_prices.csv file not found!")
    st.info("Please run crypto_tracker.py first.")
    st.stop()


df = pd.read_csv(
    file_name,
    on_bad_lines="skip"
)


# ============================================================
# CHECK COLUMNS
# ============================================================

required_columns = [
    "Name",
    "Symbol",
    "Price",
    "24h Change",
    "Market Cap",
    "Time"
]

for column in required_columns:
    if column not in df.columns:
        st.error(f"❌ Column '{column}' is missing from CSV.")
        st.stop()


# ============================================================
# REMOVE INVALID ROWS
# ============================================================

df = df[
    df["Name"].astype(str).str.strip() != "CMC20"
].copy()


# ============================================================
# CONVERT TIME
# ============================================================

df["Time"] = pd.to_datetime(
    df["Time"],
    errors="coerce"
)


# ============================================================
# CLEAN PRICE
# ============================================================

def extract_number(value):

    value = str(value)

    match = re.search(
        r"-?\d+(?:,\d{3})*(?:\.\d+)?",
        value
    )

    if match:
        number = match.group(0)
        number = number.replace(",", "")

        try:
            return float(number)
        except:
            return None

    return None


df["Price Numeric"] = df["Price"].apply(
    extract_number
)


# ============================================================
# CLEAN 24H CHANGE
# ============================================================

def extract_change(value):

    value = str(value)

    matches = re.findall(
        r"-?\d+(?:\.\d+)?\s*%",
        value
    )

    if not matches:
        return None

    first_value = matches[0]

    first_value = first_value.replace("%", "")
    first_value = first_value.strip()

    try:
        return float(first_value)
    except:
        return None


df["24h Change Numeric"] = df["24h Change"].apply(
    extract_change
)


# ============================================================
# REMOVE INVALID DATA
# ============================================================

df = df.dropna(
    subset=[
        "Time",
        "Price Numeric",
        "24h Change Numeric"
    ]
).copy()


if df.empty:
    st.error("❌ No valid cryptocurrency data found in CSV.")
    st.stop()


# ============================================================
# LATEST DATA
# ============================================================

latest = (
    df
    .sort_values("Time")
    .groupby("Symbol")
    .tail(1)
    .copy()
)


# ============================================================
# SEARCH COIN
# ============================================================

st.divider()

st.subheader("🔎 Search Cryptocurrency")

search_text = st.text_input(
    "Search by coin name or symbol:",
    placeholder="Example: Bitcoin or BTC"
)

if search_text:

    search_lower = search_text.lower().strip()

    search_result = latest[
        latest["Name"].astype(str).str.lower().str.contains(
            search_lower,
            na=False
        )
        |
        latest["Symbol"].astype(str).str.lower().str.contains(
            search_lower,
            na=False
        )
    ]

    if search_result.empty:

        st.warning(
            f"❌ No cryptocurrency found for '{search_text}'"
        )

    else:

        st.success(
            f"🔍 Found {len(search_result)} cryptocurrency(s)"
        )

        st.dataframe(
            search_result[
                [
                    "Name",
                    "Symbol",
                    "Price",
                    "24h Change",
                    "Market Cap"
                ]
            ],
            use_container_width=True,
            hide_index=True
        )


# ============================================================
# TOP INFORMATION
# ============================================================

col1, col2, col3, col4 = st.columns(4)


with col1:

    st.metric(
        "🪙 Cryptocurrencies",
        len(latest)
    )


with col2:

    latest_time = df["Time"].max()

    st.metric(
        "🕒 Latest Update",
        latest_time.strftime("%Y-%m-%d %H:%M:%S")
    )


with col3:

    top_gainer_row = latest.loc[
        latest["24h Change Numeric"].idxmax()
    ]

    top_gainer = top_gainer_row["Name"]
    top_gain = top_gainer_row["24h Change Numeric"]

    st.metric(
        "🏆 Top Gainer",
        f"{top_gainer}",
        f"+{top_gain:.2f}%"
    )


with col4:

    top_loser_row = latest.loc[
        latest["24h Change Numeric"].idxmin()
    ]

    top_loser = top_loser_row["Name"]
    top_loss = top_loser_row["24h Change Numeric"]

    st.metric(
        "📉 Top Loser",
        f"{top_loser}",
        f"{top_loss:.2f}%"
    )


# ============================================================
# LATEST PRICES
# ============================================================

st.divider()

st.subheader("📊 Latest Cryptocurrency Prices")

display_columns = [
    "Name",
    "Symbol",
    "Price",
    "24h Change",
    "Market Cap"
]

st.dataframe(
    latest[display_columns],
    use_container_width=True,
    hide_index=True
)


# ============================================================
# FILTERING
# ============================================================

st.divider()

st.subheader("🔍 Custom Price & Change Filtering")

filter_col1, filter_col2 = st.columns(2)

with filter_col1:

    min_change = st.number_input(
        "Minimum 24h Change (%)",
        value=0.10,
        step=0.10
    )

with filter_col2:

    min_price = st.number_input(
        "Minimum Price (USD)",
        value=0.0,
        min_value=0.0,
        step=1.0
    )


filtered = latest[
    (latest["24h Change Numeric"] >= min_change)
    &
    (latest["Price Numeric"] >= min_price)
]


if filtered.empty:

    st.info(
        "No cryptocurrency matches the selected conditions."
    )

else:

    st.success(
        f"Found {len(filtered)} matching cryptocurrency(s)."
    )

    st.dataframe(
        filtered[display_columns],
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# PRICE HISTORY / TREND ANALYSIS
# ============================================================

st.divider()

st.subheader("📈 Trend Analysis & Price History")

crypto_list = sorted(
    latest["Name"]
    .dropna()
    .unique()
)


if len(crypto_list) == 0:

    st.warning("No cryptocurrency names available.")

else:

    selected_crypto = st.selectbox(
        "Select a cryptocurrency:",
        crypto_list,
        key="history_crypto"
    )

    selected_data = (
        df[
            df["Name"] == selected_crypto
        ]
        .sort_values("Time")
        .copy()
    )

    if len(selected_data) < 2:

        st.warning(
            "⚠️ Not enough historical data yet."
        )

        st.info(
            "Run crypto_tracker.py for more updates."
        )

    else:

        fig = px.line(
            selected_data,
            x="Time",
            y="Price Numeric",
            markers=True,
            title=f"{selected_crypto} Price History"
        )

        price_min = selected_data[
            "Price Numeric"
        ].min()

        price_max = selected_data[
            "Price Numeric"
        ].max()

        price_range = price_max - price_min

        if price_range == 0:

            padding = abs(price_max) * 0.001

            if padding == 0:
                padding = 1

        else:

            padding = price_range * 0.20

        fig.update_layout(
            xaxis_title="Time",
            yaxis_title="Price (USD)",
            hovermode="x unified",
            height=500,
            yaxis=dict(
                range=[
                    price_min - padding,
                    price_max + padding
                ]
            )
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        st.success(
            f"📈 Trend analysis available for {selected_crypto}"
        )


# ============================================================
# CRYPTOCURRENCY STATISTICS
# ============================================================

st.subheader("📊 Cryptocurrency Statistics")

current_price = selected_data["Price Numeric"].iloc[-1]
highest_price = selected_data["Price Numeric"].max()
lowest_price = selected_data["Price Numeric"].min()
average_price = selected_data["Price Numeric"].mean()


stat1, stat2, stat3, stat4 = st.columns(4)


with stat1:

    st.metric(
        "💰 Current Price",
        f"${current_price:,.2f}"
    )


with stat2:

    st.metric(
        "📈 Highest Price",
        f"${highest_price:,.2f}"
    )


with stat3:

    st.metric(
        "📉 Lowest Price",
        f"${lowest_price:,.2f}"
    )


with stat4:

    st.metric(
        "📊 Average Price",
        f"${average_price:,.2f}"
    )


# ============================================================
# TOP GAINERS AND LOSERS
# ============================================================

st.divider()

st.subheader("📈 Market Performance")


performance_col1, performance_col2 = st.columns(2)


with performance_col1:

    st.markdown("### 🟢 Top 5 Gainers")

    top_gainers = latest.sort_values(
        "24h Change Numeric",
        ascending=False
    ).head(5)

    st.dataframe(
        top_gainers[
            display_columns
        ],
        use_container_width=True,
        hide_index=True
    )


with performance_col2:

    st.markdown("### 🔴 Top 5 Losers")

    top_losers = latest.sort_values(
        "24h Change Numeric",
        ascending=True
    ).head(5)

    st.dataframe(
        top_losers[
            display_columns
        ],
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# CRYPTOCURRENCY COMPARISON
# ============================================================

st.divider()

st.subheader("📊 Compare Cryptocurrencies")

compare_coins = st.multiselect(
    "Select cryptocurrencies to compare:",
    crypto_list,
    default=crypto_list[:2],
    key="compare_coins"
)


if len(compare_coins) < 2:

    st.info(
        "Please select at least 2 cryptocurrencies."
    )

else:

    compare_data = df[
        df["Name"].isin(compare_coins)
    ].copy()

    compare_data = compare_data.sort_values(
        "Time"
    )

    compare_fig = px.line(
        compare_data,
        x="Time",
        y="Price Numeric",
        color="Name",
        markers=True,
        title="Cryptocurrency Price Comparison"
    )

    compare_fig.update_layout(
        xaxis_title="Time",
        yaxis_title="Price (USD)",
        hovermode="x unified",
        height=500
    )

    st.plotly_chart(
        compare_fig,
        use_container_width=True
    )


# ============================================================
# PORTFOLIO / WATCHLIST
# ============================================================

st.divider()

st.subheader("💼 Portfolio / Watchlist Tracking")

watchlist = st.multiselect(
    "Add cryptocurrencies to your watchlist:",
    crypto_list,
    key="watchlist"
)


if watchlist:

    watchlist_data = latest[
        latest["Name"].isin(watchlist)
    ].copy()

    st.dataframe(
        watchlist_data[
            display_columns
        ],
        use_container_width=True,
        hide_index=True
    )

    avg_watchlist_change = (
        watchlist_data["24h Change Numeric"].mean()
    )

    st.metric(
        "📊 Average Watchlist 24h Change",
        f"{avg_watchlist_change:.2f}%"
    )

else:

    st.info(
        "Select coins above to create your personal watchlist."
    )


# ============================================================
# PRICE ALERT
# ============================================================

st.divider()

st.subheader("🔔 Custom Cryptocurrency Price Alert")

alert_crypto = st.selectbox(
    "Select cryptocurrency for price alert:",
    sorted(latest["Name"].dropna().unique()),
    key="alert_crypto"
)


alert_target = st.number_input(
    "Enter target price (USD):",
    min_value=0.0,
    value=100.0,
    step=1.0,
    key="alert_target"
)


alert_type = st.radio(
    "Alert condition:",
    [
        "Price reaches or goes above target",
        "Price falls to or below target"
    ],
    key="alert_type"
)


if st.button(
    "🔔 Check Price Alert",
    key="check_price_alert"
):

    alert_data = latest[
        latest["Name"] == alert_crypto
    ]

    if not alert_data.empty:

        alert_current_price = alert_data.iloc[0][
            "Price Numeric"
        ]

        st.write(
            f"Current price of **{alert_crypto}**: "
            f"${alert_current_price:,.2f}"
        )

        st.write(
            f"Target price: **${alert_target:,.2f}**"
        )

        if (
            alert_type
            == "Price reaches or goes above target"
        ):

            if alert_current_price >= alert_target:

                st.error(
                    f"🚨 ALERT! {alert_crypto} has reached "
                    f"${alert_current_price:,.2f}"
                )

            else:

                remaining = (
                    alert_target - alert_current_price
                )

                st.info(
                    f"⏳ Target not reached yet. "
                    f"${remaining:,.2f} remaining."
                )

        else:

            if alert_current_price <= alert_target:

                st.error(
                    f"🚨 ALERT! {alert_crypto} has fallen to "
                    f"${alert_current_price:,.2f}"
                )

            else:

                remaining = (
                    alert_current_price - alert_target
                )

                st.info(
                    f"⏳ Price is still "
                    f"${remaining:,.2f} above the target."
                )


# ============================================================
# OUTCOMES FROM PROJECT PDF
# ============================================================

st.divider()

st.subheader("🎯 Project Outcomes")

outcome1, outcome2 = st.columns(2)


with outcome1:

    st.markdown(
        """
        ### 1️⃣ Real-Time Market Monitoring
        Track the latest cryptocurrency prices,
        24-hour fluctuations and market movements.
        """
    )

    st.markdown(
        """
        ### 2️⃣ Trend Analysis
        Historical timestamped data is used to
        visualize price trends and compare
        cryptocurrency performance.
        """
    )

    st.markdown(
        """
        ### 3️⃣ Custom Alert & Filtering
        Set custom price alerts and filter
        cryptocurrencies based on price or
        percentage change.
        """
    )


with outcome2:

    st.markdown(
        """
        ### 4️⃣ Dashboard Ready
        CSV data can be connected with
        visualization tools to create an
        interactive cryptocurrency dashboard.
        """
    )

    st.markdown(
        """
        ### 5️⃣ Portfolio Tracking
        Create a personal watchlist and monitor
        important cryptocurrency metrics in
        one place.
        """
    )

    st.success(
        "✅ All major project outcomes are integrated into the dashboard."
    )


# ============================================================
# DOWNLOAD DATA
# ============================================================

st.divider()

st.subheader("📥 Download Cryptocurrency Data")

csv_data = df.to_csv(
    index=False
).encode("utf-8")


st.download_button(
    label="📥 Download CSV",
    data=csv_data,
    file_name="cryptocurrency_data.csv",
    mime="text/csv"
)


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "💡 Data is collected periodically using Selenium "
    "and stored in crypto_prices.csv"
)