import streamlit as st
import pandas as pd
from binance.client import Client
from datetime import datetime
import time, io

# Initialize Binance API client
api_key = 'xQ6ucxBVyApc2fsQ3uGIdn8Rp87YAekx1hzP9W8ZqzWw0orYasOij7RhFVU9NHVE'
api_sec = 'API KEY'
client = Client(api_key, api_sec)


# Function to fetch and process top traders data
@st.cache_data(ttl=300)
def get_top_traders():
    symbol = 'BTCUSDT'
    end_time = int(time.time() * 1000)
    start_time = end_time - (3 * 24 * 60 * 60 * 1000)

    klines = client.futures_klines(
        symbol=symbol,
        interval=Client.KLINE_INTERVAL_1HOUR,
        limit=1000,
        startTime=start_time,
        endTime=end_time
    )

    trader_data = []

    for kline in klines:
        timestamp = int(kline[0]) // 1000
        product_traded = symbol
        volume = float(kline[9])
        close_price = float(kline[4])
        open_price = float(kline[1])
        datetime_obj = datetime.fromtimestamp(timestamp)
        profit_gain = ((close_price - open_price) / open_price) * 100

        trader_data.append({
            'Trader ID': kline[5],
            'Date': datetime_obj.strftime('%Y-%m-%d'),
            'Time': datetime_obj.strftime('%H:%M:%S'),
            'Product Traded': product_traded,
            'Trading Volume (Second)': volume,
            'Profit Percentage': round(profit_gain, 2),
            'Profit Gain': round(profit_gain, 2),
            'Buying Price': open_price,
            'Selling Price': close_price,
        })

    trader_data = sorted(trader_data, key=lambda x: (x['Trading Volume (Second)'], x['Profit Percentage']),
                         reverse=True)[:7]
    return trader_data


# Function to determine trading action
def determine_trading_action(top_traders_data):
    buy_profit_threshold = 5.0
    buy_volume_threshold = 10

    sell_profit_threshold = 1.0  # (1%)
    sell_volume_threshold = 5  # 5 USDT

    for trader in top_traders_data:
        profit_percentage = trader['Profit Percentage']
        trading_volume = trader['Trading Volume (Second)']

        if profit_percentage > buy_profit_threshold and trading_volume > buy_volume_threshold:
            return 'buy'

        if profit_percentage < sell_profit_threshold and trading_volume < sell_volume_threshold:
            return 'sell'

    return 'hold'


# Streamlit UI
st.title('Top Traders Dashboard')

# Fetch and display top traders data
top_traders = get_top_traders()
st.write('Top Traders:')
st.write(pd.DataFrame(top_traders))

# Trigger trading action
if st.button('Execute Trading Actions'):
    trading_action = determine_trading_action(top_traders)
    if trading_action == 'buy':
        st.write('Buy action performed.')
        # Implement your buy logic here
    elif trading_action == 'sell':
        st.write('Sell action performed.')
        # Implement your sell logic here
    else:
        st.write('No action taken.')

top_traders = get_top_traders()
top_traders_df = pd.DataFrame(top_traders)

if st.button('Download Top Traders Data as Excel'):
    excel_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as excel_writer:
        top_traders_df.to_excel(excel_writer, sheet_name='Top_Traders', index=False)
    excel_buffer.seek(0)
    st.write("Data is being prepared for download...")

    # Offer the Excel file for download
    st.download_button(
        label='Click to Download',
        data=excel_buffer,
        file_name='top_traders_data.xlsx',  # Define the file name
        key='download_excel_button'  # Define a unique key for the button
    )

# Download individual trader reports as Excel when button is clicked
if st.button('Download Individual Trader Reports'):
    st.write('Generating and downloading individual trader reports...')
    for trader in top_traders:
        trader_id = trader['Trader ID']
        trader_df = pd.DataFrame([trader])

        excel_buffer = io.BytesIO()

        with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as excel_writer:
            trader_df.to_excel(excel_writer, sheet_name='Individual Trader', index=False)
            excel_buffer.seek(0)

            # Offer the Excel file for download with a unique key
        st.download_button(
            label=f'Download Report for Trader {trader_id}',
            data=excel_buffer,
            file_name=f'trader_{trader_id}_report.xlsx',
            key=f'download_excel_button_{trader_id}'
            )

    # st.success('Individual reports generated and downloaded successfully.')

# Run the Streamlit app
if __name__ == '__main__':
    # st.set_page_config(layout="wide")
    st.write('Running Streamlit app...')
