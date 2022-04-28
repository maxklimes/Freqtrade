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
import pandas_ta

"""
Strategy idea:

Using RSI and Bollinger Band indicators to determine whether a security is overbought
or oversold, which we can then use as buy or sell signals.

RSI (relative strength index) evaluates the magnitude of recent price changes,
which can determine if a security is overbought or oversold. Overbought and oversold
basically means the level of "saturation" in the market. For example, a security being labeled as overbought
might be experiencing too much "hype" and will be soon turning bearish (price going down) and heading for a price
correction (coming back to it"s "real" price). On the other hand, an oversold security has been dismissed way too much
and might be turning bullish (price going up) to again correct it"s price.

RSI returns a value from 0 to 100, zero being the most oversold and 100 being extremely overbought. In normal
market conditions, overbought and oversold signals usually exist around 60-70 and 20-35 respectively. 
I will be using 70 and 30, which are both widely used values, but you can of course play around as you wish.

Bollinger bands also define if a security is overbought or oversold, but they take the form of
deviations from a security's SMA (simple moving average) with a period of 20 days. The bands then
offer a valuable insight into the security, because the closer the security's price is to the upper band,
the more overbought it is and the opposite way around for the lower band. Please note that Bollinger Bands are
a little hard to understand, so please read this article from investopedia that explains everything with pictures.
https://www.investopedia.com/terms/b/bollingerbands.asp


"""


# This class is a sample. Feel free to customize it.
class BBandsRSI(IStrategy):
    """
    This is a sample strategy to inspire you.
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

    # Minimal ROI (return on investment) designed for the strategy.
    # This attribute will be overridden if the config file contains "minimal_roi".
    # The dict key symbolises minutes passed since the trade's opening
    # and the value represents being the minimum profit percentage for the trade to automatically close.

    minimal_roi = {
        "30": 0.1, 
        "0": 0.2
    }

    # Optimal stoploss designed for the strategy.
    # This attribute will be overridden if the config file contains "stoploss".
    # This will force sell any trade that exceeds a loss of your defined percentage

    stoploss = -0.15

    # Optimal timeframe for the strategy.
    timeframe = "30m"

    # Run "populate_indicators()" only for new candle.
    process_only_new_candles = False

    # General trading rules, no need to change
    use_sell_signal = True
    sell_profit_only = False
    ignore_roi_if_buy_signal = False

    # Number of candles the strategy requires before producing valid signals
    startup_candle_count: int = 30

    # Optional order type mapping.
    
    order_types = {
        "buy": "limit",
        "sell": "limit",
        "stoploss": "market",
        "stoploss_on_exchange": False
    }

    plot_config = {

        # Here we can adjust settings for plotting data directly from the terminal
        # using the freqtrade plot-dataframe command (see documentation)

        "main_plot": 
        {
            "bb_lowerband": {"color": "grey"},
            "bb_upperband": {"color": "grey"},
            "bb_middleband": {"color": "red"}
        },
        "subplots": 
        {
            "RSI": 
            {
                "rsi": {"color": "blue"},
                "overbought": {"color": "red"},
                "oversold": {"color": "green"}
            }
        }
    }

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:

        """
        Here we can define all our required datapoints (dataframes) that we'll need when executing our strategy.
        Please uncomment only dataframes you'll really use, as any surplus ones will just waste your CPU and memory.

        ex: dataframe["your_name"] = your calculation or indicator from a library
        ex: dataframe["sma3"] = ta.SMA(dataframe, timeperiod=3)

        """
        # RSI
        dataframe["rsi"] = ta.RSI(dataframe)
        dataframe["overbought"] = 70
        dataframe["oversold"] = 30

        # Bollinger Bands
        bollinger = qtpylib.bollinger_bands(qtpylib.typical_price(dataframe), window=20, stds=2)
        dataframe["bb_lowerband"] = bollinger["lower"]
        dataframe["bb_middleband"] = bollinger["mid"]
        dataframe["bb_upperband"] = bollinger["upper"]
        dataframe["bb_percent"] = (
            (dataframe["close"] - dataframe["bb_lowerband"]) /
            (dataframe["bb_upperband"] - dataframe["bb_lowerband"])
        )
        dataframe["bb_width"] = (
            (dataframe["bb_upperband"] - dataframe["bb_lowerband"]) / dataframe["bb_middleband"]
        )

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
                (dataframe["rsi"] < dataframe["oversold"]) &
                (dataframe["close"] < dataframe ["bb_lowerband"]) &
                (dataframe["volume"] > 0)  # Make sure Volume is not 0
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
                (dataframe["rsi"] > dataframe["overbought"]) &
                (dataframe["volume"] > 0)  # Make sure Volume is not 0
            ),
            "sell"] = 1
        return dataframe
