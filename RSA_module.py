#'Crypto' is more secure for this application as opposed to native 'number' or 'random' Python libs
from Crypto.Util.number import getPrime, inverse, GCD
from Crypto.Random import get_random_bytes

#"Raw" RSA implementation for academic purposes - NOT real-world usage. This is suitable for real-world: https://pycryptodome.readthedocs.io/en/latest/src/public_key/public_key.html
class RSA:
    def __init__(self, bit_length, public_key=None, modulus=None):
        if public_key is not None and modulus is not None: #Use externally provided public key and modulus (no private key)
            self.public_key = public_key
            self.modulus = modulus
        else: #Generate an N-bit (roughly) public and private key pair
            p = getPrime(bit_length//2)
            q = getPrime(bit_length//2)
            while p == q: #Ensure p != q
                q = getPrime(bit_length//2)
            n = p*q
            phi = (p-1)*(q-1)

            e = 65537  #Public exponent e; 65537 is standard for a number of reasons, mostly because it is likely to be coprime (share no common factors except 1) to phi
            if GCD(e, phi) != 1: #Fallback: generate a random e < phi that is coprime to phi
                e = getPrime(bit_length//2)
                while GCD(e, phi) != 1 or e >= phi:
                    e = getPrime(bit_length//2)

            d = inverse(e, phi) #Private exponent

            self.modulus = n #Modulus
            self.public_key = e #Public key = (Public exponent = e, modulus = n)
            self.private_key = d #Private key = private exponent = d = inverse(e, phi)

    def encrypt(self, message):
        return pow(message, self.public_key, self.modulus)

    def decrypt(self, encrypted_message):
        return pow(encrypted_message, self.private_key, self.modulus)