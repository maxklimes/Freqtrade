# pragma pylint: disable=missing-docstring, invalid-name, pointless-string-statement
# flake8: noqa: F401
# isort: skip_file
# --- Do not remove these libs ---
import numpy as np  # noqa
import pandas as pd  # noqa
from pandas import DataFrame

from freqtrade.strategy import (BooleanParameter, CategoricalParameter, DecimalParameter,
                                IStrategy, IntParameter)

# --------------------------------
# Add your lib to import here
import talib.abstract as ta
import freqtrade.vendor.qtpylib.indicators as qtpylib

"""
Strategy idea:

Using short and long term simple moving averages (SMA) and their crossovers as sell or buy points.
The basic rule of thumb with SMA is that a security trading above it's SMA is in an uptrend,
whereas a security trading below it's SMA experiences a downtrend. The SMA period dictates the "weight" of the
trend, meaning that a 5-day SMA might indicate a short term trend, while a 20-day SMA indicates a long-term one.

This strategy uses so-called SMA crossovers. It follows two types of indicators, a 50-day short term SMA and a 200-day long term one.
Whenever the 50-day SMA's value crosses above the value of the 200 day SMA, the strategy identifies something called a golden cross, which is
a bullish signal and thus indicates that the value might continue on rising. 

Conversely, when the value of the short-term SMA crosses below the value of the 200-day SMA, the strategy identifies a death cross,
a bearish signal indicating further value losses.

Other options for this strategy are a longer timeframe paired with longer SMA periods. Stock traders often use a 50-day SMA paired with a 200-day SMA
trading on a one day timeframe.

"""




# This class is a sample. Feel free to customize it.
class SMAcross(IStrategy):
    """
    More information in https://www.freqtrade.io/en/latest/strategy-customization/

    You can:
        :return: a Dataframe with all mandatory indicators for the strategies
    - Rename the class name (Do not forget to update class_name)
    - Add any methods you want to build your strategy
    - Add any lib you need to build your strategy

    You must keep:
    - the lib in the section "Do not remove these libs"
    - the methods: populate_indicators, populate_buy_trend, populate_sell_trend
    You should keep:
    - timeframe, minimal_roi, stoploss, trailing_*
    """
    # Strategy interface version - allow new iterations of the strategy interface.
    # Check the documentation or the Sample strategy to get the latest version.
    
    INTERFACE_VERSION = 2

    # Optimal timeframe for the strategy.
    
    timeframe = "1h"

    # Minimal ROI (return on investment) designed for the strategy.
    # This attribute will be overridden if the config file contains "minimal_roi".
    # The dict key symbolises minutes passed since the trade's opening
    # and the value represents being the minimum profit percentage for the trade to automatically close

    minimal_roi = {
        "60": 0.01,
        "30": 0.02,
        "0": 0.04

    #This configuration will therefore:
        #Sell whenever a 4% profit is achieved
        #Sell when a 2% profit is achieved, but only after 20 minutes
        #Sell when a 1% profit is achieved, but onyl after an hour

    }

    # Optimal stoploss designed for the strategy.
    # This attribute will be overridden if the config file contains "stoploss".
    # This will force sell any trade that exceeds a loss of your defined percentage

    stoploss = -0.10

    # Run "populate_indicators()" only for new candle.
    process_only_new_candles = False

    # General trading rules, no need to change
    use_sell_signal = True
    sell_profit_only = False
    ignore_roi_if_buy_signal = False

    # Number of candles the strategy requires before producing valid signals
    startup_candle_count: int = 30

    # Optional order type mapping, no need to adjust these
    order_types = {
        "buy": "limit",
        "sell": "limit",
        "stoploss": "market",
        "stoploss_on_exchange": False
    }

    @property
    def plot_config(self):
        return {
            # Here we can adjust settings for plotting data directly from the terminal
            # using the freqtrade plot-dataframe command (see documentation)

            "main_plot":
            {

                "sma50" : {"color" : "green"},
                "sma200" : {"color" : "blue"},

            },
            "subplots": 
            {

            #these will show up as separate graphs displaying data

            }
        }

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Here we can define all our required datapoints (dataframes) that we'll need when executing our strategy.
        Please uncomment only dataframes you'll really use, as any surplus ones will just waste your CPU and memory.

        ex: dataframe["your_name"] = your calculation or indicator from a library
        ex: dataframe["sma3"] = ta.SMA(dataframe, timeperiod=3)

        """

        # # EMA - Exponential Moving Average
        # dataframe["ema3"] = ta.EMA(dataframe, timeperiod=3)
        # dataframe["ema5"] = ta.EMA(dataframe, timeperiod=5)
        # dataframe["ema10"] = ta.EMA(dataframe, timeperiod=10)
        # dataframe["ema21"] = ta.EMA(dataframe, timeperiod=21)
        #dataframe["ema50"] = ta.EMA(dataframe, timeperiod=50)
        # dataframe["ema100"] = ta.EMA(dataframe, timeperiod=100)
        #dataframe["ema200"] = ta.EMA(dataframe, timeperiod=200)

        # # SMA - Simple Moving Average
        # dataframe["sma3"] = ta.SMA(dataframe, timeperiod=3)
        #dataframe["sma5"] = ta.SMA(dataframe, timeperiod=5)
        #dataframe["sma10"] = ta.SMA(dataframe, timeperiod=10)
        #dataframe["sma20"] = ta.SMA(dataframe, timeperiod=20)
        dataframe["sma50"] = ta.SMA(dataframe, timeperiod=50)
        # dataframe["sma100"] = ta.SMA(dataframe, timeperiod=100)
        dataframe["sma200"] = ta.SMA(dataframe, timeperiod=200)

        dataframe["golden_cross"] = qtpylib.crossed_above((dataframe["sma50"]), (dataframe["sma200"]))
        dataframe["death_cross"] = qtpylib.crossed_below((dataframe["sma50"]) , (dataframe["sma200"]))

        return dataframe

    def populate_buy_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Here we define what our strategy sees as a possible buy signal.
        We can play around with values of different indicators, crossovers and
        any other possible analysis points you might find interesting.

        ex: (my_dataframe > 54)

        """
        dataframe.loc[
            (
                (qtpylib.crossed_above((dataframe["sma50"]), (dataframe["sma200"]))) &
                (dataframe["volume"] > 0)  # Make sure Volume is not 0, NEVER DELETE THIS LINE
            ),
            "buy"] = 1

        return dataframe

    def populate_sell_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Here we define what our strategy sees as a possible sell signal.
        We can play around with values of different indicators, crossovers and
        any other possible analysis points you might find interesting.
        Please note that the stoploss and roi (return on investment) in % that you 
        previously defined will also trigger a sell signal, so you can leave
        this field empty if you choose to do so.

        ex: (my_dataframe < 54)

        """
        dataframe.loc[
            (
                (qtpylib.crossed_below((dataframe["sma50"]) , (dataframe["sma200"]))) &
                (dataframe["volume"] > 0)  # Make sure Volume is not 0, NEVER DELETE THIS LINE
            ),
            "sell"] = 1
        return dataframe
    