# Blocknotify Processing Developer Certification Level 1
##### January 2022
The New Fork
Commit: 11 Nov 2021 0faa8d8 master branch

<br>

## Prerequisites
Data from the customer has passed through the pipeline and is saved in the import-api database. See Appendix A for details along with the source code of the import-api (private repo) or api-import (public repo)

<br>

## Control Flow
### Initialization

#### Sentry
##### _What is Sentry?_
Sentry is a self-hosted and cloud-based application monitoring that helps software teams to see clearer, solve quicker, & learn continuously.
<br>

#### Imports
##### _The openfood lib vs other imports_

<br>

#### Script version & other variables
##### _Why use a script version variable?_

<br>

#### Explorers
##### _What is an explorer?_
Explorer is a blockchain search engine that allows you to search for a particular piece of information in the blockchain. The activities carried out on crypto blockchains are known as transactions, which occur when cryptocurrencies are sent to and from wallet addresses.
<br>

### Start of control flow
#### Processing Batches
##### _Why get batches with no timestamp?_

<br>

#### Batch data
##### _How to generate a timestamp?_
##### _How to generate a wallet?_
Run this command inside simple-working folder:
> docker-compose run blocknotify-python /code/new_org_wallet $(echo -n "_PARAPHRASE_" | sha256sum)

Change the _PARAPHRASE_ to your preferred own paraphrase (i.e. Welcome to Juicy Chain). This will be used as a wallet password and an additional random encrypt value.

##### _What is an R-Address?_
A generally used wallet address.

##### _Why generate a wallet for the batch?_
All batches must make a wallet address to be imported to Blockchain.

##### _How & why generate an “integrity start” transaction?_
##### _How, why & what is the significance of batch linking functionality?_
All batches are linked to each other across organisations. Batch linking function allows us to see the journey history of each batch, which batches were used in a product, and where the batch came from.
##### _Why use a “this node R-Address”?_
To distinguish the organisation address from the other address.

<br>

#### Offline wallets
##### _Why is it called an “offline wallet”?_
There is an address needed to lead data to the blockchain. So, blocknotify will create new wallet addresses based on organisation addresses that are not used for any manual transaction but for data import requirements only.

##### _What is a “hot wallet” (“full node wallet”, “native wallet”)?_
##### _Why are there so many sendToBatchXXX functions?_
Each batch data has a different value. We separate all of these into a different function.
##### _What does sendToBatchXXX do and what are the similarities & differences between some of these functions?_
sendToBatchXXX based on sendToBatch() logic. Basically, this is used to send the batch data to the blockchain. The differences are in the type of value. But we can handle it by logic at this moment. 

<br>

#### Certificates
##### _What are certificates?_
It will contain certification data that helps consumers and suppliers adopt the highest standards in food safety, meet your regulatory requirements and contractual obligations, and gain access to global markets.

##### _Why would a certificate have a timestamp or no timestamp & why does it matter?_
##### _Why is there a function called “patchWrapper”?_
To wrap up a request method supported by the HTTP protocol for making partial changes to an existing resource.
<br>

#### Locations
##### _What is a location?_
##### _Where is location data stored?_
##### _Why would a location have a timestamp of no timestamp & why does it matter?_

<br>

#### State of processing
##### _There are 11 switches (all set to false or 0) for managing the state of the processing. What are they and what is their meaning?_
##### _What is a housekeeping tx?_
##### _What does the housekeeping tx enable for reporting?_

<br>

# Appendix A
After data is sent to the *-pipeline, it is then added to the respective organisations import-database.
The data sent and stored are the following fields:
| Field | Description                     |
| ----- | ------------------------------- |
| anfp  | article number finished product |
| dfp   | description finished product    |
| bnfp  | batch number finished product   |
| pds   | production day start            |
| pde   | production day end              |
| jds   | julian day start                |
| jde   | julian day end                  |
| bbd   | best before date                |
| pc    | production country              |
| pl    | production location             |
| rmn   | raw material number             |
| pon   | purchase order number           |
| pop   | purchase order location         |

**pon -** this number is what is actually used to track supplies across different organisations.
**bnfp -** this number is organisation specific, it is used to track items within an organisation.

<br>

#### Wallets
Wallets are at the center of how we use blockchains to trace supply lines.
Some key wallets are:
| Wallet | Description                    |
| ------  | ------------------------------- |
| THIS_NODE_RADDRESS  | This is the organisations wallet  |
| customer_pool_wallet   | This is the Global PO (product order aka pon) wallet. As mentioned above, the pon stays the same between different orgs, and this wallet exists so that all the orgs to send a transaction to it    |
| pool_batch_wallet  | This can be thought of as the organisations wallet |
| pool_po   | This is the orgs PO wallet |

These wallets are static and are integral to tracking the supply lines.

<br>

##### _Generated Wallets_
Wallets can be generated from any piece of data (see gen_wallet() in openfood.py). 
This is done in a deterministic and reproducable way. 
For some of the field values, we use their value to generate a wallet. Those wallets are a representation of that field and its value.
| Wallet | Description                    |
| ------  | ------------------------------- |
| bnfp_wallet  | Wallet is generated from the bnfp value  |
| pl_wallet   | Wallet generated from location to send 10k satoshis to bnfp_wallet |

<br>

##### _Offline Wallets_
These are wallets that are used to send values (in the form of satoshis) to the bnfp_wallet.
| Wallet | Description                     |
| ----- | ------------------------------- |
| pon_wallet  | Wallet to send pon value to the bnfp_wallet |
| jds_wallet   | Wallet to send jds value to the bnfp_wallet    |
| jde_wallet  | Wallet to send jde value to the bnfp_wallet   |
| pc_wallet   | Wallet to send pc value to the bnfp_wallet            |
| bb_date_wallet   | Wallet to send bb value to the bnfp_wallet |
| production_date_wallet   | Wallet to send pde value to the bnfp_wallet |
| tin_wallet   | Wallet to send anfp value to the bnfp_wallet  |
| mass_balance_wallet   | Wallet to send pon value to the bnfp_wallet |

<br>

#### Blocknotify Sequence
Blocknotify is triggered on a cron job periodicaly (~10 minutes).
The job of blocknotify is to:
1. Create bnfp wallet.
2. Create an integrity wallet.
3. Fund the integrity wallet, funds are sent from the organisation wallet to the integrity wallet this is to signal that the blocknotify process has started, analogous to a timestamp.
4. Add the integrity transaction to the import-api integrity table (linked to the batch table).
5. Create one-to-many transaction from orgs wallet to:
    * The pon (as satoshis) gets sent to the global PO wallet.
    * The pon (as satoshis) gets sent to the org PO wallet.
    * The bnfp (as satoshis) gets sent to the org batch wallet.
    * 10k satoshis are sent to the bnfp wallet.

    The value (as satoshis) are sent from their respective wallets, to the bnfp_wallet the above transaction, along with the integrity wallet address are added to the tstx table.

Certificates:
* Each certificate is read and turned into a wallet.
* 10k satoshis are sent to the certificate wallet from the bnfp wallet


![Blocknotify Processing Developer Certification Level 1](https://user-images.githubusercontent.com/87051701/149473775-a7118e84-aa7f-4f6a-b614-174e88173f9a.jpg)


# Generate list.json
example command
```
docker run  -i -t instance-100_blocknotify-python /code/new_list_json > list.json
cat list.json | jq '.'
```
