import yfinance as yf
import mplfinance as mpf

__all__ = ["generate_chart"]

def generate_chart(symbol, entry=None, stop=None, tps=None):
    ticker = yf.Ticker(symbol + "-USD")
    hist = ticker.history(period="3mo")

    addplots = []
    if entry:
        addplots.append(mpf.make_addplot([entry]*len(hist), color="g", linestyle="--"))
    if stop:
        addplots.append(mpf.make_addplot([stop]*len(hist), color="r", linestyle="--"))
    if tps:
        colors = ["b", "c", "m", "y"]
        for i, (k, v) in enumerate(tps.items()):
            addplots.append(mpf.make_addplot([v]*len(hist), color=colors[i], linestyle="--"))

    filepath = f"{symbol}.png"
    mpf.plot(
        hist,
        type="candle",
        style="charles",
        title=f"{symbol} - גרף יומי",
        savefig=filepath,
        addplot=addplots
    )
    return filepath
