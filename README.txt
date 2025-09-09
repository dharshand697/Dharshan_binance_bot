Binance Trading Bot

A Python-based automated trading bot for Binance that helps execute
cryptocurrency trades based on predefined logic.

Features

-   Connects to Binance API
-   Automated trading strategies
-   Logging of trade activity
-   Easy setup with requirements file

Project Structure

    ├── requirement.txt     # Required Python packages
    ├── run_bot.bat         # Batch script to start the bot (Windows)
    ├── src/
    │   └── bot.py          # Main bot script
    ├── bot.log             # Log file (runtime generated)
    └── venv/               # Virtual environment (not recommended to commit)

Installation

1.  Clone the repository:

        git clone https://github.com/yourusername/keerthi-binance-bot.git
        cd keerthi-binance-bot

2.  Create and activate a virtual environment:

        python -m venv venv
        source venv/bin/activate   # On Linux/Mac
        venv\Scripts\activate      # On Windows

3.  Install dependencies:

        pip install -r requirement.txt

Usage

1.  Configure your Binance API keys inside the bot script (src/bot.py)
    or using environment variables.

2.  Run the bot:

        python src/bot.py

    Or on Windows:

        run_bot.bat

Logs

-   All runtime logs are stored in bot.log.

Notes

-   Ensure you have a Binance account and API keys set up.
-   Use testnet or paper trading before running with real funds.
-   Do not commit your API keys to the repository.

License

This project is licensed under the MIT License. Feel free to use and
modify it.
