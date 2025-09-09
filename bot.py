import os
import argparse
import logging
from logging.handlers import RotatingFileHandler
from binance.client import Client
from binance.exceptions import BinanceAPIException

# ------------------ Logging ------------------
def setup_logging(logfile="bot.log"):
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        fmt = logging.Formatter("%(asctime)s %(levelname)s - %(message)s")
        fh = RotatingFileHandler(logfile, maxBytes=5_000_000, backupCount=3)
        fh.setFormatter(fmt)
        logger.addHandler(fh)
        ch = logging.StreamHandler()
        ch.setFormatter(fmt)
        logger.addHandler(ch)

setup_logging()
logger = logging.getLogger(__name__)

# ------------------ Bot Class ------------------
class BasicBot:
    def __init__(self, api_key, api_secret, testnet=True):
        if testnet:
            self.client = Client(api_key, api_secret, testnet=True)
            self.client.FUTURES_URL = "https://testnet.binancefuture.com/fapi/v1"
        else:
            self.client = Client(api_key, api_secret)
        logger.info("Bot started (testnet=%s)", testnet)

        # ✅ Validate API keys immediately
        self._validate_api_keys()

    def _validate_api_keys(self):
        try:
            balance = self.client.futures_account_balance()
            logger.info("API key validation successful. Balance fetched.")
        except BinanceAPIException as e:
            logger.error("Invalid API keys! code=%s, msg=%s", e.code, e.message)
            raise SystemExit("Exiting: Invalid Binance API keys.")
        except Exception as e:
            logger.exception("Unexpected error during API key validation: %s", e)
            raise SystemExit("Exiting: Could not validate Binance API keys.")

    def _safe_call(self, fn, **kwargs):
        try:
            result = fn(**kwargs)
            logger.info("API call success: %s %s", fn.__name__, kwargs)
            return result
        except BinanceAPIException as e:
            logger.error("BinanceAPIException: code=%s msg=%s", e.code, e.message)
            return None
        except Exception as e:
            logger.exception("Unexpected error: %s", e)
            return None

    # --- Utility to check balance ---
    def check_balance(self):
        return self._safe_call(self.client.futures_account_balance)

    # --- Orders ---
    def place_market(self, symbol, side, qty):
        return self._safe_call(
            self.client.futures_create_order,
            symbol=symbol, side=side, type="MARKET", quantity=qty
        )

    def place_limit(self, symbol, side, qty, price):
        return self._safe_call(
            self.client.futures_create_order,
            symbol=symbol, side=side, type="LIMIT",
            quantity=qty, price=str(price), timeInForce="GTC"
        )

    def place_stop_market(self, symbol, side, qty, stop_price):
        return self._safe_call(
            self.client.futures_create_order,
            symbol=symbol, side=side, type="STOP_MARKET",
            stopPrice=str(stop_price), quantity=qty
        )

# ------------------ Simple OCO ------------------
class SimpleOCO:
    def __init__(self, bot, symbol, side, qty, tp_price, sl_price):
        self.bot = bot
        self.symbol = symbol
        self.side = side
        self.qty = qty
        self.tp_price = tp_price
        self.sl_price = sl_price

    def _opposite(self, side):
        return "SELL" if side == "BUY" else "BUY"

    def start(self):
        close_side = self._opposite(self.side)
        tp = self.bot.place_limit(self.symbol, close_side, self.qty, self.tp_price)
        sl = self.bot.place_stop_market(self.symbol, close_side, self.qty, self.sl_price)
        logger.info("Placed OCO orders")
        return {"tp": tp, "sl": sl}

# ------------------ CLI ------------------
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("symbol")
    parser.add_argument("side", choices=["BUY","SELL"])
    parser.add_argument("type", choices=["MARKET","LIMIT","OCO","BALANCE"])
    parser.add_argument("quantity", type=float, nargs="?")
    parser.add_argument("--price", type=float)
    parser.add_argument("--stop", type=float)
    parser.add_argument("--api-key")
    parser.add_argument("--api-secret")
    parser.add_argument("--testnet", action="store_true", default=True)
    args = parser.parse_args()

    api_key = args.api_key or os.getenv("BINANCE_API_KEY")
    api_secret = args.api_secret or os.getenv("BINANCE_API_SECRET")
    if not api_key or not api_secret:
        raise SystemExit("API keys required! Make sure you have testnet keys for testnet mode.")

    bot = BasicBot(api_key, api_secret, testnet=args.testnet)

    if args.type == "BALANCE":
        print(bot.check_balance())
    elif args.type == "MARKET":
        if args.quantity is None:
            raise SystemExit("Quantity required for MARKET order")
        print(bot.place_market(args.symbol, args.side, args.quantity))
    elif args.type == "LIMIT":
        if args.quantity is None or args.price is None:
            raise SystemExit("Quantity and --price required for LIMIT order")
        print(bot.place_limit(args.symbol, args.side, args.quantity, args.price))
    elif args.type == "OCO":
        if args.quantity is None or args.price is None or args.stop is None:
            raise SystemExit("OCO needs quantity, --price (TP) and --stop (SL)")
        oco = SimpleOCO(bot, args.symbol, args.side, args.quantity, args.price, args.stop)
        print(oco.start())

if __name__ == "__main__":
    main()
