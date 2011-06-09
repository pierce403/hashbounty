import bitcoin
import settings

connection = None

def reload_connection(user=None, password=None, host=None, port=None):
    global connection
    
    s = settings.Settings.get_settings()
    s.BITCOIN_USER = user     or getattr(s, "BITCOIN_USER", None) or settings.BITCOIN_USER
    s.BITCOIN_PASS = password or getattr(s, "BITCOIN_PASS", None) or settings.BITCOIN_PASS
    s.BITCOIN_HOST = host     or getattr(s, "BITCOIN_HOST", None) or settings.BITCOIN_HOST
    s.BITCOIN_PORT = port     or getattr(s, "BITCOIN_PORT", None) or settings.BITCOIN_PORT
    s.put()    
    
    connection = bitcoin.connect_to_remote(
      s.BITCOIN_USER,
      s.BITCOIN_PASS,
      s.BITCOIN_HOST,
      port=s.BITCOIN_PORT,
    )
    
    print connection.proxy._ServiceProxy__serviceURL

reload_connection()
