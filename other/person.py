from cryptography.hazmat.primitives.asymmetric import ec


class Person:
    secret_key: ec.EllipticCurvePrivateKey
    public_key: ec.EllipticCurvePublicKey

    def __init__(self):
        self.secret_key = ec.generate_private_key(curve=ec.BrainpoolP256R1())
        self.public_key = self.secret_key.public_key()

