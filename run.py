import os
import sentry_sdk
# Setup sentry, normall all this would ago after the imports, but the imports are crashing
sentry_dsn = os.getenv('SENTRY_DSN')
if sentry_dsn:
    sentry_sdk.init(
        sentry_dsn,
        environment=os.environ['ENVIRONMENT']
    )
    sentry_sdk.set_tag('org', os.environ['SENTRY_ORG'])

import json
# import pytest
# import os
from ofc-openfood import openfood
from ofc-openfood.openfood_env import EXPLORER_URL, EXPLORER_LIST
from ofc-openfood.openfood_env import IMPORT_API_BASE_URL
from ofc-openfood.openfood_env import DEV_IMPORT_API_RAW_REFRESCO_INTEGRITY_PATH
from ofc-openfood.openfood_env import DEV_IMPORT_API_RAW_REFRESCO_TSTX_PATH
from ofc-openfood.openfood_env import openfood_API_BASE_URL
from ofc-openfood.openfood_env import openfood_API_ORGANIZATION_CERTIFICATE
from ofc-openfood.openfood_env import openfood_API_ORGANIZATION_LOCATION
from ofc-openfood.openfood_env import openfood_API_ORGANIZATION_BATCH
from ofc-openfood.openfood_env import HK_LIB_VERSION
from ofc-openfood.openfood_env import HK_SKIP_BATCH_PROCESSING
from ofc-openfood.openfood_env import HK_BATCH_PROCESSING

from dotenv import load_dotenv
load_dotenv(verbose=True)

SCRIPT_VERSION = HK_LIB_VERSION
URL_IMPORT_API_RAW_REFRESCO_INTEGRITY_PATH = IMPORT_API_BASE_URL + DEV_IMPORT_API_RAW_REFRESCO_INTEGRITY_PATH
URL_IMPORT_API_RAW_REFRESCO_TSTX_PATH = IMPORT_API_BASE_URL + DEV_IMPORT_API_RAW_REFRESCO_TSTX_PATH
URL_openfood_API_ORGANIZATION_BATCH = openfood_API_BASE_URL + openfood_API_ORGANIZATION_BATCH

if EXPLORER_URL:
    print("Explorer URL: {EXPLORER_URL}")
else:
    print("Unable to select one of the explorers!")
    print(json.dumps(EXPLORER_LIST, sort_keys=True, indent=4))
    print("- Check explorers url correctness")
    print("- Check explorers syncronization to smart chain")
    exit()

def process_batches():
    batches_no_timestamp = openfood.get_batches_no_timestamp()
    wallet_sent = {
        'PON': False,
        'JDS': False,
        'JDE': False,
        'PC': False,
        'BBD': False,
        'PDS': False,
        'TIN': False,
        'MB': False,
        'PL': False
    }
    for batch in batches_no_timestamp:
        try:
            print("""
            
            =====>>>>> STAGE: Batch processing start
            
            """)
            print(batch)
            # batch_wallets_integrity holds integrity address, batch by import_id, batch_lot_raddress
            batch_wallets_integrity = openfood.batch_wallets_generate_timestamping(batch, batch['id'])
            # not sure why this tofix is here dec2020
            tofix_bnfp_wallet = openfood.gen_wallet(batch['bnfp'], "bnfp")
            integrity_id = batch_wallets_integrity['id']
            integrity_start_txid = openfood.batch_wallets_fund_integrity_start(batch_wallets_integrity['integrity_address'])
            print("** txid ** (Timestamp integrity start): " + integrity_start_txid)
            openfood.batch_wallets_timestamping_start(batch_wallets_integrity, integrity_start_txid)
            # sendmany_txid = openfood.organization_send_batch_links(batch_wallets_integrity)
            # sendmany_txid = openfood.organization_send_batch_links2(batch_wallets_integrity, batch['pon'])
            sendmany_txid = openfood.organization_send_batch_links3(batch_wallets_integrity, batch['pon'], batch['bnfp'])
            # openfood.timestamping_save_batch_links(integrity_id, sendmany_txid)
            print(integrity_id)
            print(openfood.get_this_node_raddress())
            print(sendmany_txid)
            openfood.save_batch_timestamping_tx(integrity_id, "ORG WALLET", openfood.get_this_node_raddress(), sendmany_txid)
        except Exception as e:
            print("## ERROR FULL NODE TX")
            print("# bailing out of tx sending to BATCH_LOT")
            print("# integrity timestamp started, but not finished sending tx")
            print("# Check balances of Organization wallet")
            print("# Exiting")
            print("##")
            openfood.log2discord("EXITING; ERROR FULL NODE " + openfood.get_this_node_raddress()+ " BATCH LINKING TX: " + str(e))
            exit()


            # Offline wallets
        print("""
            
        =====>>>>> STAGE: Send offline wallets into batch
        
        """)

        try:
            txid_pon = openfood.sendToBatchPON(tofix_bnfp_wallet['address'], batch['pon'], integrity_id)
            print("** txid ** (PON): " + txid_pon)
            if txid_pon:
                wallet_sent['PON'] = True
                print('PON has been funded')
            txid_julian_start = openfood.sendToBatchJDS(tofix_bnfp_wallet['address'], batch['jds'], integrity_id)
            print("** txid ** (JULIAN START): " + txid_julian_start)
            if txid_julian_start:
                wallet_sent['JDS'] = True
                print('JDS has been funded')
            txid_julian_stop = openfood.sendToBatchJDE(tofix_bnfp_wallet['address'], batch['jde'], integrity_id)
            print("** txid ** (JULIAN STOP): " + txid_julian_stop)
            if txid_julian_stop:
                wallet_sent['JDE'] = True
                print('JDE has been funded')
            txid_origin_country = openfood.sendToBatchPC(tofix_bnfp_wallet['address'], batch['pc'], integrity_id)
            print("** txid ** (ORIGIN COUNTRY): " + txid_origin_country)
            if txid_origin_country:
                wallet_sent['PC'] = True
                print('PC has been funded')
            txid_bb_date = openfood.sendToBatchBBD(tofix_bnfp_wallet['address'], batch['bbd'], integrity_id)
            print("** txid ** (BB DATE): " + txid_bb_date)
            if txid_bb_date:
                wallet_sent['BBD'] = True
                print('BBD has been funded')
            txid_prod_date = openfood.sendToBatchPDS(tofix_bnfp_wallet['address'], batch['pds'], integrity_id)
            print("** txid ** (PROD DATE): " + txid_prod_date)
            if txid_prod_date:
                wallet_sent['PDS'] = True
                print('PDS has been funded')
            # GS1 GTIN is anfp in this batch implementation, TIN trade id number
            txid_tin = openfood.sendToBatchTIN(tofix_bnfp_wallet['address'], batch['anfp'], integrity_id)
            print("** txid ** (TIN): " + txid_tin)
            if txid_tin:
                wallet_sent['TIN'] = True
                print('TIN has been funded')
            txid_mass = openfood.sendToBatchMassBalance( tofix_bnfp_wallet['address'], batch['mass'], integrity_id)
            print("** txid  ** (MASS): " + txid_mass)
            if txid_mass:
                wallet_sent['MB'] = True
                print('MB has been funded')
            txid_pl = openfood.sendToBatchPL(tofix_bnfp_wallet['address'], batch['pl'], integrity_id)
            print("** txid ** (PL): " + txid_pl)
            if txid_pl:
                wallet_sent['PL'] = True
                print('PL has been funded')

            update_wallet_sent = openfood.save_offline_wallet_sent(integrity_id, wallet_sent)
            if update_wallet_sent: print('Integrity Updated!')
            
        except Exception as e:
            print("## ERROR OFFLINE WALLET TX")
            print("# bailing out of tx sending to BATCH_LOT")
            print("# Check balances of Organization offline wallets")
            print("# Exiting")
            print("##")
            openfood.log2discord("EXITING; ERROR OFFLINE WALLET TX: " + str(e))
            exit()

        print("""
            
        =====>>>>> STAGE: Certificates for batch
            
        """)

        try:
            jc_organization = openfood.get_jcapi_organization()
            jc_org_id = jc_organization['id']
            all_certificate_data = openfood.get_all_certificate_for_organization(jc_org_id)
            # this can all be put into an openfood lib function like sendToBatchDeliveryDate
            # early-dev all_certificate_data = openfood.get_all_certificate_for_batch()
            # loop
    #        for certificate_data in all_certificate_data:
    #            print(certificate_data)
    #            c_txid = openfood.send_to_batch_certificate(tofix_bnfp_wallet['address'], certificate_data, integrity_id)
    #            openfood.timestamping_save_certificate(id, "CERTIFICATE WALLET", offline_wallet, c_txid)
    #            print("** txid ** (Certificate to batch_lot): " + c_txid)

        except Exception as e:
            print(e)
            print("## ERROR OFFLINE SENDING TX")
            print("# bailing out of tx sending to BATCH_LOT")
            print("# integrity timestamp started, but not finished sending tx")
            print("# Check balances of Organization wallets including certificate, location, etc")
            print("# Warning: Not implemented yet - resume operation")
            print("# Exiting")
            print("##")
            openfood.log2discord(e)
            exit()

        try:
            print("Push data from import-api to openfood-api for batch_lot")
            jcapi_batch = openfood.push_batch_data_consumer(jc_org_id, batch, tofix_bnfp_wallet)
            integrity_end_txid = openfood.batch_wallets_fund_integrity_end(batch_wallets_integrity['integrity_address'])
            print("** txid ** (Timestamp integrity end): " + integrity_end_txid)
            openfood.batch_wallets_timestamping_end(batch_wallets_integrity, integrity_end_txid)

        except Exception as e:
            print(e)
            print("### ERROR IMPORT-API PUSH TO openfood-API")
            print("# CHECK openfood-API")
            print("# Exiting")
            print("##")

    return len(batches_no_timestamp)

def process_certificates():
    print("Getting certificates requiring timestamping")
    jc_organization = openfood.get_jcapi_organization()
    jc_org_id = jc_organization['id']

    certificates_no_timestamp = openfood.get_certificates_no_timestamp(jc_org_id)

    for certificate in certificates_no_timestamp:
        # print("** certificate with no raddress (timestamping/creation/register/fund) **")
        # print(certificate)
        offline_wallet = openfood.offlineWalletGenerator_fromObjectData_certificate(certificate)
        url = openfood_API_BASE_URL + openfood_API_ORGANIZATION_CERTIFICATE + str(certificate['id']) + "/"
        # TODO a better multi utxo funding option (possible offline wallet to fund these types of "JIT" funding
        funding_txid = openfood.fund_certificate(offline_wallet['address'])
        funding_txid = openfood.fund_certificate(offline_wallet['address'])
        funding_txid = openfood.fund_certificate(offline_wallet['address'])
        funding_txid = openfood.fund_certificate(offline_wallet['address'])
        funding_txid = openfood.fund_certificate(offline_wallet['address'])
        data = {"raddress": offline_wallet['address'], "pubkey": offline_wallet['pubkey'], "txid_funding": funding_txid}
        openfood.patchWrapper(url, data=data)
        return funding_txid


def process_locations():
    print("Getting location requiring timestamping")
    jc_organization = openfood.get_jcapi_organization()
    jc_org_id = jc_organization['id']

    locations_no_timestamp = openfood.get_locations_no_timestamp(jc_org_id)

    for location in locations_no_timestamp:
        # print("** location with no raddress (timestamping/creation/register/fund) **")
        # print(location)
        offline_wallet = openfood.offlineWalletGenerator_fromObjectData_location(location)
        url = openfood_API_BASE_URL + openfood_API_ORGANIZATION_LOCATION + str(location['id']) + "/"
        # TODO a better multi utxo funding option (possible offline wallet to fund these types of "JIT" funding
        funding_txid = openfood.fund_location(offline_wallet['address'])
        funding_txid = openfood.fund_location(offline_wallet['address'])
        funding_txid = openfood.fund_location(offline_wallet['address'])
        funding_txid = openfood.fund_location(offline_wallet['address'])
        funding_txid = openfood.fund_location(offline_wallet['address'])
        data = {"raddress": offline_wallet['address'], "pubkey": offline_wallet['pubkey'], "txid_funding": funding_txid}
        openfood.patchWrapper(url, data=data)
        return funding_txid

# state (all false to start)
hk_txid = 0
batch_chain = 0
kv_chain = 0
batch_chain_wallet_ok = 0
kv_chain_wallet_ok = 0
kv_records_ok = 0
funding_txid = 0
synced = 0
certificates_processed = 0
locations_processed = 0
batches_processed = 0
print("***Start of processing*** SCRIPT VERSION: " + str(SCRIPT_VERSION))

# connect to nodes
batch_chain = openfood.connect_batch_node()
kv_chain = openfood.connect_kv1_node()

if batch_chain:
    print("===> Batch chain connect ok, checking node wallet")
    batch_chain_wallet_ok = openfood.check_node_wallet()
if kv_chain:
    print("===> KV chain connect ok, checking node wallet")
    kv_chain_wallet_ok = openfood.check_kv1_wallet()
if kv_chain_wallet_ok:
    print("====> KV wallet ok, checking KV records")
    kv_records_ok = openfood.verify_kv_pool_wallets()
if batch_chain_wallet_ok:
    print("====> Batch chain wallet ok, checking offline wallets")
    funding_txid = openfood.check_offline_wallets()
if batch_chain_wallet_ok:
    print("====> Batch chain wallet ok, checking sync")
    synced = openfood.check_sync()
if synced:
    print("=====> Batch node synced, checking certificates & locations")
    certificates_processed = process_certificates()
    locations_processed = process_locations()
if certificates_processed or locations_processed or funding_txid:
    print(str(HK_SKIP_BATCH_PROCESSING) + " (HK) ======> Batch chain skipping batch processing: offline wallets funded, certificates, locations processed")
    hk_txid = openfood.housekeeping_tx(HK_SKIP_BATCH_PROCESSING)
if not certificates_processed and not locations_processed and not funding_txid:
    print("=======> Batch chain ready to process batches")
    batches_processed = process_batches()
if not certificates_processed and not locations_processed and not batches_processed and not funding_txid:
    print(str(SCRIPT_VERSION) + " (HK) ========> Batch chain no certificates or locations or no batches to process")
    hk_txid = openfood.housekeeping_tx(SCRIPT_VERSION)
if batches_processed:
    print(str(HK_BATCH_PROCESSING) + " (HK) ========> Batch chain batches processed ok")
    hk_txid = openfood.housekeeping_tx(HK_BATCH_PROCESSING)
# leave next line in commnted out plz
# openfood.organization_get_pool_wallets_by_raddress(openfood.get_this_node_raddress()) # works
print("House keeping tx:", hk_txid, sep="\n")
print("End of script - Done")

