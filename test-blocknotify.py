import unittest
# load_dotenv(verbose=True)
from pathlib import Path  # Python 3.6+ only
from dotenv import load_dotenv
env_path = Path('.') / '.env.test'
load_dotenv(dotenv_path=env_path)
from ofc-openfood import juicychain
from ofc-openfood.juicychain_env import KOMODO_NODE
from ofc-openfood.juicychain_env import RPC_USER
from ofc-openfood.juicychain_env import RPC_PASSWORD
from ofc-openfood.juicychain_env import RPC_PORT
from ofc-openfood.juicychain_env import TEST_THIS_NODE_WALLET
from ofc-openfood.juicychain_env import TEST_GEN_WALLET_PASSPHRASE
from ofc-openfood.juicychain_env import TEST_GEN_WALLET_ADDRESS
from ofc-openfood.juicychain_env import TEST_GEN_WALLET_WIF
from ofc-openfood.juicychain_env import TEST_GEN_WALLET_PUBKEY
# from ofc-openfood.juicychain_env import EXPLORER_URL


class TestBlocknotify(unittest.TestCase):

    def test_gen_wallet(self):
        '''
        Tests wallet generation returns good stuff
        '''
        print(TEST_THIS_NODE_WALLET)
        juicychain.connect_node(RPC_USER, RPC_PASSWORD, KOMODO_NODE, RPC_PORT)
        new_wallet = juicychain.gen_wallet(TEST_THIS_NODE_WALLET, TEST_GEN_WALLET_PASSPHRASE, "TEST WALLET")
        # self.assertEqual("asdf", "asdf")
        self.assertEqual(TEST_GEN_WALLET_ADDRESS, new_wallet['address'], "ERROR: something changed!")
        self.assertEqual(TEST_GEN_WALLET_WIF, new_wallet['wif'], "ERROR: something changed!")
        self.assertEqual(TEST_GEN_WALLET_PUBKEY, new_wallet['pubkey'], "ERROR: something changed!")


if __name__ == '__main__':
    unittest.main()
