import bitcoin
import settings

connection = bitcoin.connect_to_remote(
  settings.BITCOIN_USER,
  settings.BITCOIN_PASS,
  settings.BITCOIN_HOST,
  port=settings.BITCOIN_PORT,
)

