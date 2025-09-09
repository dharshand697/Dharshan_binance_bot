@echo off
REM --- Set Binance API keys ---
set binance_API_KEY=e7b19da25a30accbdaa9da8a102c8e6e45e063f46c886db35f68865ea542216a
set binance_API_SECRET=c548996d9cf95fa066c70da871f304f80721b2797cd8f29dc0cd3bbda7e02234

REM --- Activate virtual environment ---
call venv\Scripts\activate

REM --- Run the bot (example: Market BUY order) ---
python src\bot.py BTCUSDT BUY MARKET 0.01 --testnet

pause
