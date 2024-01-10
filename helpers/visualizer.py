import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import mplfinance as mpf
import matplotlib.dates as mdates
from datetime import datetime
from models.settings import Settings
import os
import time
import helpers.telegr as tel
import helpers.services as serv
import talib
import exchange_workers.binance as bin
import matplotlib
matplotlib.use('agg')

binance_dark = {
    "base_mpl_style": "dark_background",
    "marketcolors": {
        "candle": {"up": "#3dc985", "down": "#ef4f60"},  
        "edge": {"up": "#3dc985", "down": "#ef4f60"},  
        "wick": {"up": "#3dc985", "down": "#ef4f60"},  
        "ohlc": {"up": "green", "down": "red"},
        "volume": {"up": "#247252", "down": "#82333f"},  
        "vcedge": {"up": "green", "down": "red"},  
        "vcdopcod": False,
        "alpha": 1,
    },
    "mavcolors": ("#ad7739", "#a63ab2", "#62b8ba"),
    "facecolor": "#1b1f24",
    "gridcolor": "#2c2e31",
    "gridstyle": "--",
    "y_on_right": True,
    "rc": {
        "axes.grid": True,
        "axes.grid.axis": "y",
        "axes.edgecolor": "#474d56",
        "axes.titlecolor": "red",
        "figure.facecolor": "#161a1e",
        "figure.titlesize": "x-large",
        "figure.titleweight": "semibold",
    },
    "base_mpf_style": "binance-dark",
}

def _add_candlestick_labels(ax, ohlc):
    transform = ax.transData.inverted()
    text_pad = transform.transform((0, 10))[1] - transform.transform((0, 0))[1]
    percentages = 100. * (ohlc.close - ohlc.open) / ohlc.open
    kwargs = dict(horizontalalignment='center', color='#FFFFFF', fontsize=6)
    for i, (idx, val) in enumerate(percentages.items()):
        if val != np.nan:
            row = ohlc.loc[idx]
            open = row.open
            close = row.close
            if open < close:
                ax.text(i, row.high + text_pad, np.round(val, 1), verticalalignment='bottom', **kwargs)
            elif open > close:
                ax.text(i, row.low - text_pad, np.round(val, 1), verticalalignment='top', **kwargs)

def ensure_directory_exists(path: str):
    if not os.path.exists(path):
        os.makedirs(path)
    else:
        serv.remove_files(path)

async def create_and_send_chart(settings: Settings, duration_min: int, signal: int, profit_loss: float):
    coin = settings.coin
    timeframe = settings.timeframe
    chunk = bin.get_kline(coin, 120, timeframe)
    closes = chunk[:, 4]
    highs = chunk[:, 2]
    lows = chunk[:, 3]

    rsi = talib.RSI(closes, timeperiod=24)
    plus_di = talib.PLUS_DI(highs, lows, closes, timeperiod=24)
    minus_di = talib.MINUS_DI(highs, lows, closes, timeperiod=24)
    adx = talib.ADX(highs, lows, closes, timeperiod=24)

    ensure_directory_exists(f'chart_{settings.name}/{coin}')

    description = f'coin: {coin} tf: {timeframe} sg: {signal} dur: {duration_min} profit: {profit_loss}'
    save_candlesticks_indic_2vol(rsi[-60:], plus_di[-60:], minus_di[-60:], adx[-60:], chunk[-60:], f'chart_{settings.name}/{coin}/pic.png', description)
    time.sleep(1)
    await tel.send_inform_message(settings.collector_bot, description, f'chart_{settings.name}/{coin}/pic.png', True)

def save_candlesticks_indic_2vol(rsi:list, adx: list, plus_di:list, minus_di:list, candles: list, path: str, description: str):
    # Convert the candlesticks data into a pandas DataFrame
    df = pd.DataFrame(candles, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms', utc=False).dt.tz_localize('UTC').dt.tz_convert('Europe/London')
    df.set_index('timestamp', inplace=True)

    # Create a DataFrame for the indicators
    df_indicators = pd.DataFrame(index=df.index)
    df_indicators['rsi'] = pd.Series(rsi, index=df.index[-len(rsi):])
    df_indicators['adx'] = pd.Series(adx, index=df.index[-len(adx):])
    df_indicators['plus_di'] = pd.Series(plus_di, index=df.index[-len(plus_di):])
    df_indicators['minus_di'] = pd.Series(minus_di, index=df.index[-len(minus_di):])

    # Define the style dictionary
    my_style = mpf.make_mpf_style(base_mpf_style='binance', gridstyle='')

    # Create a subplot for the indicators
    apds = [mpf.make_addplot(df_indicators[col], panel=1, secondary_y=False) for col in df_indicators.columns]

    # Add volume to the plot
    apds.append(mpf.make_addplot(df['volume'], panel=2, secondary_y=False, color='g'))

    # Plot the candlestick chart using mpf.plot()
    mpf.plot(df, type='candle', style=my_style, axisoff=True, figratio=(4,4), savefig=path, addplot=apds, panel_ratios=(1,1,0.5), title=description)


# def draw_candlesticks(candles: list, type_labels: str, mark_index: int):
#     # Convert the candlesticks data into a pandas DataFrame
#     df = pd.DataFrame(candles, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
#     df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms', utc=False).dt.tz_localize('UTC').dt.tz_convert('Europe/London')
#     df.set_index('timestamp', inplace=True)
#     figsize = (10, 6)
#     # Plot the candlestick chart using mpf.plot()
#     fig, axlist = mpf.plot(df, type='candle', style=binance_dark, title=f'Type: {type_labels}', returnfig=True, figsize=figsize)

#     # Add percentage labels to the candlestick chart
#     # _add_candlestick_labels(axlist[0], df)

#     # if type_labels == 'up':
#     #     axlist[0].annotate('MARK', (mark_index, df.iloc[mark_index]['open']), xytext=(mark_index, df.iloc[mark_index]['open']-10),
#     #                 arrowprops=dict(facecolor='black', arrowstyle='->'))
#     # elif type_labels == 'down':
#     #     axlist[0].annotate('MARK', (mark_index, df.iloc[mark_index]['open']), xytext=(mark_index, df.iloc[mark_index]['open']+10),
#     #                     arrowprops=dict(facecolor='black', arrowstyle='->'))

#     # Display the chart
#     mpf.show()

# def draw_graph(values):
#     periods = range(1, len(values) + 1)
#     plt.plot(periods, values)
#     plt.xlabel('Period')
#     plt.ylabel('Value')
#     plt.title('Graph for Values')
#     plt.show()

# def plot_time_series(data_list: list, save_pic: bool, date_line: str):
#     path = f'pic/{datetime.now().date().strftime("%Y-%m-%d")}'
#     timestamps = [item[0] for item in data_list]
#     values = [item[1] for item in data_list]
    
#     dates = [datetime.fromtimestamp(ts/1000) for ts in timestamps]
#     fig, ax = plt.subplots()
#     ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
#     ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
#     plt.xticks(rotation=45)
#     periods = range(1, len(values) + 1)
    
#     ax.plot(dates, values)
    
#     plt.xlabel('Period')
#     plt.ylabel('Value')
#     plt.title('Graph for Values')

#     for i, (date, value) in enumerate(zip(dates, values)):
#         if i % 25 == 0:
#             ax.text(date, value, f"{i}", verticalalignment='top', horizontalalignment='center', fontsize=9, color='red')

#     # Convert date_line to a datetime object
#     date_line = datetime.strptime(date_line, '%d.%m.%y')
#     # Determine the index of the date_line in the dates list
#     try:
#         date_line_index = next(i for i, date in enumerate(dates) if date > date_line)
#     except StopIteration:
#         date_line_index = 0

#     # Draw a red line after the date_line
#     if date_line_index != 0:
#         for i, (date, value) in enumerate(zip(dates, values)):
#             if i == date_line_index:
#                 ax.text(date, value, f"{i}", verticalalignment='top', horizontalalignment='center', fontsize=9, color='red')
#             elif i == date_line_index + 1:
#                 ax.axvline(x=date, linestyle='--', color='red')
    
#     plt.tight_layout()

#     if save_pic:
#         if not os.path.exists(path):
#             os.makedirs(path)
#         end_path = f'{path}/{datetime.now().timestamp()}.png'
#         plt.savefig(end_path)
#         return end_path
#     return None