import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend


class AES:
    """
    A utility class for AES-256 encryption and decryption using CBC mode.
    Pads/truncates keys to 32 bytes (256 bits) automatically.
    """

    @staticmethod
    def encrypt(data: bytes, key: bytes) -> bytes:
        """
        Encrypts data using AES-256 in CBC mode.
        The IV is prepended to the ciphertext.

        Args:
            data (bytes): The plaintext data to encrypt.
            key (bytes): The encryption key. Will be padded/truncated to 32 bytes.

        Returns:
            bytes: The IV concatenated with the ciphertext.
        """
        # 32 bytes (256 bits) for AES-256
        # If the key is shorter, it's padded with null bytes.
        # If it's longer, it's truncated.
        if len(key) < 32:
            key = key.ljust(32, b'\0')
        elif len(key) > 32:
            key = key[:32]

        # Pad the data to a multiple of AES block size (16 bytes)
        # PKCS7 padding is used to ensure the plaintext length is a multiple of the block size.
        padder = padding.PKCS7(algorithms.AES.block_size).padder()
        padded_data = padder.update(data) + padder.finalize()

        iv = os.urandom(16)

        # Create an AES cipher object with CBC mode
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()

        # Encrypt the padded data
        encrypted_data = encryptor.update(padded_data) + encryptor.finalize()

        # Return the IV prepended to the encrypted data.
        # The IV is necessary for decryption and is not secret.
        return iv + encrypted_data

    @staticmethod
    def decrypt(encrypted_data: bytes, key: bytes) -> bytes:
        """
        Decrypts data encrypted with AES-256 in CBC mode.

        Args:
            encrypted_data (bytes): The IV concatenated with the ciphertext.
            key (bytes): The decryption key. Will be padded/truncated to 32 bytes.

        Returns:
            bytes: The decrypted plaintext data.

        Raises:
            ValueError: If decryption fails (e.g., incorrect key, corrupted data, bad padding).
        """
        # Ensure key is 32 bytes (256 bits) for AES-256
        if len(key) < 32:
            key = key.ljust(32, b'\0')
        elif len(key) > 32:
            key = key[:32]

        # Extract the IV (first 16 bytes) from the encrypted data
        iv = encrypted_data[:16]
        ciphertext = encrypted_data[16:]

        # Create an AES cipher object for decryption
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()

        # Decrypt the ciphertext
        padded_data = decryptor.update(ciphertext) + decryptor.finalize()

        # Unpad the data
        unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
        try:
            data = unpadder.update(padded_data) + unpadder.finalize()
        except ValueError as e:
            # This error typically indicates incorrect padding, which often means
            # the key was wrong or the data was corrupted.
            raise ValueError("Decryption failed: Incorrect padding or corrupted data. Key might be wrong.") from e

        return data
