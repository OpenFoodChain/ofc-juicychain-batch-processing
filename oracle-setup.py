from openfood_lib_dev import openfood
import json
import time

print(openfood.connect_batch_node())
openfood.check_node_wallet()


balance = openfood.explorer_get_balance("RD7cYALdPMWDhZ3wF1u6fkgFciqLKx8usW")
if balance == 0:
    print("you have to get coins to set it up. Balance is now: ", + str(balance))
else:
    print("balance is enough: " + str(balance))


res = openfood.oracle_create("test1", "this is a big test je weet zelf", 's')


if res['result'] == "success":
    print("oracle successfully created " + res["hex"])
else:
    print("oracle creation failed " + res["hex"])

hexvalue = res["hex"]

print("now we put it on the blockchain ")

res = openfood.sendrawtxwrapper(hexvalue)

print("the transaction of our oracle: " + res)

print("now we fund the oracle ")
oracletxid = res
res = openfood.oracle_fund(oracletxid)
print("oracle tx created: " + str(res))
fundtx = res['hex']
res = openfood.sendrawtxwrapper(fundtx)
print("oracle tx send: " + str(res))

#substransactionsend = res

#res = openfood.gettransactionwrapper(substransactionsend)

#while res['confirmations'] < 1:
#    print("let's try again ")
#    time.sleep(30)
#    res = openfood.gettransactionwrapper(substransactionsend)   



print("now we register as publisher of the oralce: ")


res = openfood.oracle_register(oracletxid, "0.1" )

print("oracle registerd: " + str(res))
registerhex = res['hex']

res = openfood.sendrawtxwrapper(registerhex)

print("tx send: " + res)
print("get publisher id")

res = openfood.oracle_info(oracletxid)
while len(res['registered']) == 0:
    print("let's try again ")
    time.sleep(30)
    res = openfood.oracle_info(oracletxid)   

print("oracle info is: " + str(res) )

print("now we subscribe to the oracle ")

publisherid = res['registered'][0]['publisher']
res = openfood.oracle_subscribe(oracletxid, publisherid, '1')

subscribehex = res['hex']
res = openfood.sendrawtxwrapper(subscribehex)

print("subscription succsess: " + str(res))
teststring = "teststring"
finalstring = "0a"
teststring = teststring.encode('utf-8')
teststring = teststring.hex()
print(teststring)
finalstring = finalstring + teststring


print(finalstring)

res = openfood.oracle_data(oracletxid, finalstring) 

print(res)

while res['result'] == 'error':
    print("we will try again")
    time.sleep(30)
    res = openfood.oracle_data(oracletxid, finalstring) 
    print(res)

datapublishtxid = res['hex']
res = openfood.sendrawtxwrapper(datapublishtxid)

print(res)

print("oracle has been set up correctly and a test string has been broadcasted, on the oracle owned by this nodes wallet")
print("now use the other scripts to publish more, or subscirbe, the info you need will be printed on the screen")
finalobject = {}
finalobject['oracletxid'] = oracletxid
finalobject['publisherid'] = publisherid
print(finalobject)


