
from ofc-openfood import openfood
import json
import time
import sys

print("welcome to the publishing script")
if len(sys.argv) < 3: 
    print("the oracle or string is missing")
    exit()

print("we are going to publish on this oracle: " + sys.argv[1])
print("we are going to publish this string: " + sys.argv[2])

print(openfood.connect_batch_node())
openfood.check_node_wallet()



teststring = sys.argv[2]
finalstring = hex(len(teststring))

teststring = teststring.encode('utf-8')
teststring = teststring.hex()
finalstring = finalstring[2:] + teststring
oracletxid = sys.argv[1]

print(finalstring)

res = openfood.oracle_data(oracletxid, finalstring)

print(res)

if not 'hex' in res:
    print("error encountered")
    exit()



datapublishtxid = res['hex']
res = openfood.sendrawtxwrapper(datapublishtxid)

print("txid of oracle publish is: " + res)

print("end of the script, if you get an error check if the oracle exists and if there is a subscription on the oracle")
