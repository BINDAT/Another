from bitcoin import encode, decode, random_key
from bitcoin.wallet import CBitcoinSecret, P2PKHBitcoinAddress
from bitcoin.core import lx, COIN, b2lx
from bitcoin.core.key import CPubKey
from bitcoin.core.script import CScript
from bitcoin.core import CMutableTransaction, CMutableTxIn, CMutableTxOut, COutPoint

# Créer une clé privée et une clé publique
secret_exponent = random_secret_exponent()
private_key = secret_exponent.get_private()
public_key = secret_exponent.get_public()

# Créer une transaction
tx = Tx()
tx.add_input("bc1qpefjryqs8ms77p72cze9qmtcsxu4tp99vzzr94", 0.001, secret_exponent)
tx.add_output("1Aa1Q1Q1Q1Q1Q1Q1Q1Q1Q1Q1Q1Q1Q1Q1Q1Q1Q1Q1",0.0005)

# Signer la transaction
tx.sign(private_key)

# Valider la transaction
if tx.verify():
    print("Transaction validée avec succès!")
else:
    print("Transaction invalide.")

# Envoyer la transaction
tx.send("http://localhost:8332","1Aa1Q1Q1Q1Q1Q1Q1Q1Q1Q1Q1Q1Q1Q1Q1Q1Q1Q1Q1")

print("Transaction envoyée avec succès!")