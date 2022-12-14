<?php

// https://github.com/BitcoinPHP/BitcoinECDSA.php
require_once 'BitcoinECDSA.php/src/BitcoinPHP/BitcoinECDSA/BitcoinECDSA.php';
use BitcoinPHP\BitcoinECDSA\BitcoinECDSA;

class BitcoinECDSADecker extends BitcoinECDSA {

    /***
     * Tests if the address is valid or not.
     *
     * @param string $address (base58)
     * @return bool
     */
    public function validateAddress($address)
    {
        $address    = hex2bin($this->base58_decode($address));

        /*
        if(strlen($address) !== 25)
            return false;
        $checksum   = substr($address, 21, 4);
        $rawAddress = substr($address, 0, 21);
	*/

	$len = strlen($address);
        $checksum   = substr($address, $len-4, 4);
        $rawAddress = substr($address, 0, $len-4);

        if(substr(hex2bin($this->hash256($rawAddress)), 0, 4) === $checksum)
            return true;
        else
            return false;
    }

    /**
     * Returns the current network prefix for WIF, '80' = main network, 'ef' = test network.
     *
     * @return string (hexa)
     */
    public function getPrivatePrefix($PrivatePrefix = 128){

        if($this->networkPrefix =='6f')
            return 'ef';
        else
           return sprintf("%02X",$PrivatePrefix);
    }
    /***
     * returns the private key under the Wallet Import Format
     *
     * @return string (base58)
     * @throws \Exception
     */

    public function getWIF($compressed = true, $PrivatePrefix = 128)
    {
        if(!isset($this->k))
        {
            throw new \Exception('No Private Key was defined');
        }

        $k          = $this->k;
        
        while(strlen($k) < 64)
            $k = '0' . $k;
        
        $secretKey  =  $this->getPrivatePrefix($PrivatePrefix) . $k;
        
        if($compressed) {
            $secretKey .= '01';
        }
        
        $secretKey .= substr($this->hash256(hex2bin($secretKey)), 0, 8);

        return $this->base58_encode($secretKey);
    }
}

$bitcoinECDSA = new BitcoinECDSADecker();

$passphrase = $argv[1];
$passphraseIndex = $argv[2];
#$passphrase = "here";

/* available coins, you can add your own with params from src/chainparams.cpp */

$coins = Array(
    Array("name" => "KMD",  "PUBKEY_ADDRESS" => 60, "SECRET_KEY" => 188)
);

$k = hash("sha256", $passphrase);
$k = pack("H*",$k);
$k[0] = Chr (Ord($k[0]) & 248); 
$k[31] = Chr (Ord($k[31]) & 127); 
$k[31] = Chr (Ord($k[31]) | 64);
$k = bin2hex($k);

$bitcoinECDSA->setPrivateKey($k);
//echo "             Passphrase: '" . $passphrase . "'" . PHP_EOL;
//echo PHP_EOL;
echo "[$passphraseIndex,";

foreach ($coins as $coin) {

if (is_array($coin["PUBKEY_ADDRESS"])) {
      $NetworkPrefix = bin2hex(implode("",array_map("chr", $coin["PUBKEY_ADDRESS"])));
      $bitcoinECDSA->setNetworkPrefix($NetworkPrefix);
} else
      $bitcoinECDSA->setNetworkPrefix(sprintf("%02X", $coin["PUBKEY_ADDRESS"])); 

// Returns the compressed public key. The compressed PubKey starts with 0x02 if it's y coordinate is even and 0x03 if it's odd, the next 32 bytes corresponds to the x coordinates.
//$NetworkPrefix = $bitcoinECDSA->getNetworkPrefix();

//echo "\x1B[01;37m[\x1B[01;32m "  . $coin["name"] . " \x1B[01;37m]\x1B[0m" . PHP_EOL;
$address = $bitcoinECDSA->getAddress(); //compressed Bitcoin address
echo "\"" . sprintf("%34s",$bitcoinECDSA->getPubKey()) . "\",\"" . $bitcoinECDSA->getWIF( true, $coin["SECRET_KEY"]) . "\",\"" . sprintf("%34s",$address) . "\"" ; #. PHP_EOL;
}
echo "]";

?>
