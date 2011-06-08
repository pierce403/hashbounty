import bitcoin
import settings

connection = None

def reload_connection(user=None, password=None, host=None, port=None):
    global connection
    
    s = settings.Settings.get_settings(
        BITCOIN_USER = user or settings.BITCOIN_USER,
        BITCOIN_PASS = password or settings.BITCOIN_PASS,
        BITCOIN_HOST = host or settings.BITCOIN_HOST,
        BITCOIN_PORT = port or settings.BITCOIN_PORT,
    )
    
    connection = bitcoin.connect_to_remote(
      s.BITCOIN_USER,
      s.BITCOIN_PASS,
      s.BITCOIN_HOST,
      port=s.BITCOIN_PORT,
    )
    
    print connection.proxy._ServiceProxy__serviceURL

reload_connection()
