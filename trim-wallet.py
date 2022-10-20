

address = THIS_NODE_RADDRESS
wif = THIS_NODE_WIF
to_address = "RS7y4zjQtcNv7inZowb8M6bH3ytS1moj9A"
utxos_json = json.loads(openfood.explorer_get_utxos(address))
# send all amount from 2 utxos
test = openfood.utxo_send(utxos_json[0:2], 'all', to_address, wif, address)
