import yfinance as yf
from db import Database

class TickerManager:

    # iniciador de bd
    def __init__(self):
        self.db = Database('bot.db')
        self._create_table()

    def _create_table(self):
        self.db.execute('''
            CREATE TABLE IF NOT EXISTS tickers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT UNIQUE NOT NULL,
                alert_up REAL,
                alert_down REAL
            )
        ''')

    # helpers de metodos
    def _get_ticker_info(self, symbol) -> dict:
        t = yf.Ticker(symbol)
        return {
            "price": t.info.get('regularMarketPrice'),
            "currency": t.info.get('currency')
        }

    def _ticker_exists(self, symbol) -> bool:
        try:
            t = yf.Ticker(symbol)
            return t.info.get('regularMarketPrice') is not None
        except Exception:
            return False

    def _ticker_in_db(self, symbol) -> bool:
        return self.db.fetch_one('SELECT 1 FROM tickers WHERE symbol = ?', (symbol,)) is not None

    def _data_in_table(self) -> bool:
        return self.db.fetch_one('SELECT 1 FROM tickers LIMIT 1') is not None

    def _alert(self, alert_type):
        if alert_type == "up":
            return "alert_up"
        elif alert_type == "down":
            return "alert_down"
        elif alert_type == "all":
            return "all"
        else:
            raise ValueError("Tipo de alerta no válido. Use 'up', 'down' o 'all'.")
    
    def _get_alerts(self, symbol):
        alert_up = self.db.fetch_one('SELECT alert_up FROM tickers WHERE symbol = ?', (symbol,))
        alert_down = self.db.fetch_one('SELECT alert_down FROM tickers WHERE symbol = ?', (symbol,))
        return (alert_up[0] if alert_up else None, alert_down[0] if alert_down else None)
    
    # metodos principales
    def add_ticker(self, symbol) -> str:
        if not self._ticker_exists(symbol):
            return f"Ticker {symbol} is not valid or does not exist on Yahoo Finance."
        elif self._ticker_in_db(symbol):
            return f"Ticker {symbol} already exists in the database."
        else:
            ticker = self._get_ticker_info(symbol)
            self.db.execute("INSERT INTO tickers (symbol) VALUES (?)", (symbol,))
            return f"Ticker added!! {symbol}: ${ticker['price']} {ticker['currency']}"

    def del_ticker(self, symbol) -> str:
        if not self._ticker_in_db(symbol):
            return f"Ticker {symbol} does not exist in the database."
        else:
            self.db.execute("DELETE FROM tickers WHERE symbol = ?", (symbol,))
            return f"Ticker {symbol} eliminated!!."

    def show_ticker(self, symbol) -> str:
        try:
            ticker = self._get_ticker_info(symbol)
            return f"{symbol}: ${ticker['price']} {ticker['currency']}"
        except Exception:
                return f"{symbol} (Error al obtener precio)"
       
    def list_tickers(self) -> str:
        if self._data_in_table():
            tickers = self.db.fetch_all("SELECT symbol FROM tickers")
            list = ""
            for ticker in tickers:
                try:
                    tdata = self._get_ticker_info(ticker[0])
                    list += f"{ticker[0]}: ${tdata['price']} {tdata['currency']}\n"
                except Exception:
                    list += f"{ticker[0]} (Error al obtener precio)\n"
            return list
        else:
            return "La lista de tickers está vacía."
    
    def add_alert(self, symbol, alert_type, price):
        if self._ticker_in_db(symbol):
            alert = self._alert(alert_type)
            self.db.execute('UPDATE tickers SET {} = ? WHERE symbol = ?'.format(alert), (price, symbol))
            return f"Alerta '{alert_type}' para {symbol} establecida en ${price}."
        else:
            return f"El ticker '{symbol}' no se encuentra en la lista."
    
    def del_alert(self, symbol, alert_type):
        if self._get_alerts(symbol) != (None, None):
            alert = self._alert(alert_type)
            alerts = self._get_alerts(symbol)
            if alert == "alert_up" and alerts[0] is not None:
                self.db.execute('UPDATE tickers SET alert_up = NULL WHERE symbol = ?', (symbol,))
            elif alert == "alert_down" and alerts[1] is not None:
                self.db.execute('UPDATE tickers SET alert_down = NULL WHERE symbol = ?', (symbol,))
            elif alert == "all":
                self.db.execute('UPDATE tickers SET alert_up = NULL, alert_down = NULL WHERE symbol = ?', (symbol,))
            else:
                return f"No hay alerta '{alert_type}' establecida para {symbol}."
            return f"Alerta '{alert_type}' para {symbol} eliminada."
        else:
            return f"El ticker '{symbol}' no se encuentra en la lista."
            
    def show_alerts(self):
        messages = []
        for ticker in self.db.fetch_all("SELECT symbol FROM tickers"):
            if self._get_alerts(ticker[0]) != (None, None):
                alerts = self._get_alerts(ticker[0])
                alert_up = alerts[0]
                alert_down = alerts[1]
                message = f"Alertas para {ticker[0]}:\n"
                message += f"Alerta de subida: {'No establecida' if alert_up is None else f'${alert_up}'}\n"
                message += f"Alerta de bajada: {'No establecida' if alert_down is None else f'${alert_down}'}"
                messages.append(message)
        return "\n\n".join(messages) if messages else "No hay alertas establecidas para ningún ticker."

    def check_alerts(self) -> str:
        messages = []
        alerts = self.db.fetch_all(
            "SELECT symbol, alert_up, alert_down FROM tickers "
            "WHERE alert_up IS NOT NULL OR alert_down IS NOT NULL"
        )
        for symbol, alert_up, alert_down in alerts:
            ticker = self._get_ticker_info(symbol)
            price = ticker["price"]
            currency = ticker["currency"]
            if price is None:
                messages.append(f"No se pudo comprobar la alerta de {symbol}: precio actual no disponible.")
                continue
            if alert_up is not None and price >= alert_up:
                messages.append(
                    f"ALERTA: {symbol} ha subido a ${price} {currency}, "
                    f"superando el límite de ${alert_up}."
                )
            if alert_down is not None and price <= alert_down:
                messages.append(
                    f"ALERTA: {symbol} ha bajado a ${price} {currency}, "
                    f"alcanzando el límite de ${alert_down}."
                )
        return "\n\n".join(messages) if messages else "No hay alertas activadas en este momento."