import cv2
import numpy as np
import json
import zlib
import base64
import os

# Import the AES encryption class from your backend
from backend.encryption import AES


class DCTSteganography:
    """
    Implements a hybrid DCT-LSB steganography method with AES encryption
    and metadata embedding (data type, filename).
    """

    def __init__(self, quantization_step=16):  # MODIFIED: Reverted quantization_step to 16
        self.block_size = 8
        self.quantization_step = quantization_step
        # Define metadata keys for consistency
        self.METADATA_KEY_TYPE = "type"
        self.METADATA_KEY_CONTENT = "content"
        self.METADATA_KEY_FILENAME = "filename"
        self.METADATA_KEY_FILEEXT = "file_extension"
        self.TEXT_TYPE = "text"
        self.FILE_TYPE = "file"

        # Define specific low-frequency AC coefficients to use for embedding/extraction
        # These are chosen to be less visually sensitive than DC component (0,0)
        # and provide good capacity. Total 8 coefficients per 8x8 block.
        self.coefficients_to_use = [
            (0, 1), (1, 0),  # Horizontal and Vertical low-freq AC
            (1, 1),  # Diagonal low-freq AC
            (0, 2), (2, 0),  # Next set of horizontal/vertical
            (2, 1), (1, 2),  # Next set of diagonal
            (0, 3)  # Another low-freq horizontal
        ]
        self.bits_per_block_per_channel = len(self.coefficients_to_use)

    def _to_binary(self, data_bytes: bytes) -> str:
        """Converts bytes data to a binary string."""
        return ''.join(format(byte, '08b') for byte in data_bytes)

    def _to_bytes(self, binary_string: str) -> bytes:
        """Converts a binary string back to bytes."""
        bytes_list = [binary_string[i:i + 8] for i in range(0, len(binary_string), 8)]
        return bytes(int(b, 2) for b in bytes_list if len(b) == 8)

    def embed_data(self, image_path: str, secret_data, password: str, is_text: bool,
                   original_filename: str = None, output_path: str = None) -> str:
        """
        Embeds encrypted and compressed data (text or file) into an image using DCT-LSB.

        Args:
            image_path (str): Path to the cover image (must be PNG).
            secret_data (Union[str, bytes]): The secret text (str) or file content (bytes) to embed.
            password (str): The password for AES encryption.
            is_text (bool): True if secret_data is text, False if it's binary file content.
            original_filename (str, optional): Original filename if embedding a file.
            output_path (str, optional): Path where the generated stego image will be saved.

        Returns:
            str: Path to the generated stego image.

        Raises:
            ValueError: If image not found, format unsupported, data too large, or if not a PNG.
        """
        if not image_path.lower().endswith('.png'):
            raise ValueError("Only PNG images are supported for embedding to prevent data loss from compression.")

        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Image not found or unsupported format: {image_path}")

        # --- PREPARATION: Metadata, Serialization, Compression, Encryption ---
        # 1. Prepare metadata payload
        metadata_payload = {
            self.METADATA_KEY_TYPE: self.TEXT_TYPE if is_text else self.FILE_TYPE,
        }
        if is_text:
            data_bytes = secret_data.encode('utf-8')
            # Base64 encode all content to handle binary data consistently in JSON
            metadata_payload[self.METADATA_KEY_CONTENT] = base64.b64encode(data_bytes).decode('utf-8')
        else:
            data_bytes = secret_data  # Data is already bytes for files
            if original_filename:
                metadata_payload[self.METADATA_KEY_FILENAME] = original_filename
                _, file_extension = os.path.splitext(original_filename)
                metadata_payload[self.METADATA_KEY_FILEEXT] = file_extension.lower()
            metadata_payload[self.METADATA_KEY_CONTENT] = base64.b64encode(data_bytes).decode('utf-8')

        # 2. Serialize metadata payload to JSON string
        json_payload_str = json.dumps(metadata_payload)
        json_payload_bytes = json_payload_str.encode('utf-8')

        # 3. Compress the JSON payload
        compressed_payload_bytes = zlib.compress(json_payload_bytes, level=9)

        # 4. Encrypt the compressed payload using AES
        key_bytes = self._derive_key_from_password(password)
        encrypted_data_to_embed = AES.encrypt(compressed_payload_bytes, key_bytes)

        data_to_embed_len = len(encrypted_data_to_embed)
        data_to_embed_bits = self._to_binary(encrypted_data_to_embed)
        # --- END PREPARATION ---

        ycrcb = cv2.cvtColor(img, cv2.COLOR_BGR2YCrCb)
        channels = list(cv2.split(ycrcb))  # Get mutable list of channels

        h, w = channels[0].shape
        block_size = self.block_size
        bits_per_channel_block = self.bits_per_block_per_channel

        # Calculate total available bits
        total_available_bits = (h // block_size) * (w // block_size) * bits_per_channel_block * len(channels)

        # --- DEBUG PRINTS FOR CAPACITY ---
        print(f"\n--- EMBEDDING DEBUG ---")
        print(f"Original data size: {len(secret_data)} bytes (is_text: {is_text})")
        print(f"Compressed & Encrypted data size: {data_to_embed_len} bytes")
        print(f"Compressed & Encrypted data bits: {len(data_to_embed_bits)}")
        print(f"Image dimensions: {h}x{w} pixels")
        print(
            f"Total available bits from image ({len(channels)} channels * {bits_per_channel_block} bits/block/channel): {total_available_bits}")
        # --- END DEBUG PRINTS ---

        if len(data_to_embed_bits) > total_available_bits:
            raise ValueError(
                f"Encrypted data too large for image capacity. "
                f"Required bits: {len(data_to_embed_bits)}, Available bits: {total_available_bits}. "
                f"Consider a larger image or shorter message/file."
            )

        bit_idx = 0
        # Loop through each channel (Y, Cr, Cb)
        for channel_idx in range(len(channels)):
            if bit_idx >= len(data_to_embed_bits):
                break
            current_channel = channels[channel_idx]
            for i in range(0, h, block_size):
                for j in range(0, w, block_size):
                    if bit_idx >= len(data_to_embed_bits):
                        break
                    block = current_channel[i:i + block_size, j:j + block_size]
                    if block.shape != (block_size, block_size):  # Skip partial blocks at edges
                        continue

                    dct_block = cv2.dct(np.float32(block))

                    # Embed multiple bits per block by iterating through selected coefficients
                    for coeff_coords in self.coefficients_to_use:
                        if bit_idx >= len(data_to_embed_bits):
                            break

                        coeff_value = dct_block[coeff_coords[0], coeff_coords[1]]
                        target_bit = int(data_to_embed_bits[bit_idx])

                        # Quantization-based embedding (modify LSB of quantized coefficient)
                        quantized_coeff = int(round(coeff_value / self.quantization_step))
                        modified_quantized_coeff = quantized_coeff

                        if target_bit == 0:
                            modified_quantized_coeff = quantized_coeff - (quantized_coeff % 2)
                        else:
                            modified_quantized_coeff = quantized_coeff + 1 if quantized_coeff % 2 == 0 else quantized_coeff

                        dct_block[coeff_coords[0], coeff_coords[1]] = float(
                            modified_quantized_coeff * self.quantization_step)
                        bit_idx += 1

                    current_channel[i:i + block_size, j:j + block_size] = np.uint8(cv2.idct(dct_block).clip(0, 255))

        # Merge modified channels back
        stego_ycrcb = cv2.merge(channels)
        stego_img = cv2.cvtColor(stego_ycrcb, cv2.COLOR_YCrCb2BGR)

        # Embed the length of the *encrypted data* in LSB of the first few pixel values
        length_bits = f"{data_to_embed_len:032b}"  # 32 bits for length (up to ~536MB of payload)

        flat_img = stego_img.reshape(-1)  # Flatten the entire image pixel array
        if len(length_bits) > len(flat_img):
            raise ValueError("Image too small to embed data length in LSB of pixel values.")

        for i, bit in enumerate(length_bits):
            flat_img[i] = (flat_img[i] & 0xFE) | int(bit)

        stego_final = flat_img.reshape(stego_img.shape)

        if output_path is None:
            raise ValueError("Output path must be provided to save the stego image.")

        cv2.imwrite(output_path, stego_final)
        return output_path

    def extract_data(self, image_path: str, password: str) -> dict:
        """
        Extracts, decrypts, and decompresses hidden data from a stego image.

        Args:
            image_path (str): Path to the stego image (must be PNG).
            password (str): The password for AES decryption.

        Returns:
            dict: A dictionary containing:
                  - 'type' (str): "text" or "file"
                  - 'content' (Union[str, bytes]): The decrypted text or file content bytes.
                  - 'filename' (str, optional): Original filename if embedded a file.
                  - 'file_extension' (str, optional): Original file extension if embedded a file.

        Raises:
            ValueError: If stego image not found, extraction incomplete, decryption fails, etc.
        """
        if not image_path.lower().endswith('.png'):
            raise ValueError("Only PNG images are supported for extraction.")

        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Stego image not found: {image_path}")

        # 1. Extract length of encrypted data from LSB of first 32 pixel values
        flat_img = img.reshape(-1)
        if len(flat_img) < 32:
            raise ValueError("Stego image too small to contain 32-bit length header.")

        length_bits_list = [str(flat_img[i] & 1) for i in range(32)]
        data_to_extract_len = int(''.join(length_bits_list), 2)
        total_bits_to_extract = data_to_extract_len * 8

        # 2. Extract encrypted data bits from DCT coefficients of Y, Cr, and Cb channels
        ycrcb = cv2.cvtColor(img, cv2.COLOR_BGR2YCrCb)
        channels = cv2.split(ycrcb)  # Get channels as tuple

        h, w = channels[0].shape
        block_size = self.block_size
        extracted_bits_list = []

        # Loop through each channel (Y, Cr, Cb)
        for channel_idx in range(len(channels)):
            if len(extracted_bits_list) >= total_bits_to_extract:
                break
            current_channel = channels[channel_idx]
            for i in range(0, h, block_size):
                for j in range(0, w, block_size):
                    if len(extracted_bits_list) >= total_bits_to_extract:
                        break
                    block = current_channel[i:i + block_size, j:j + block_size]
                    if block.shape != (block_size, block_size):
                        continue

                    dct_block = cv2.dct(np.float32(block))

                    # Extract multiple bits per block by iterating through selected coefficients
                    for coeff_coords in self.coefficients_to_use:
                        if len(extracted_bits_list) >= total_bits_to_extract:
                            break

                        coeff_value = dct_block[coeff_coords[0], coeff_coords[1]]
                        quantized_coeff = int(round(coeff_value / self.quantization_step))
                        bit = quantized_coeff % 2
                        extracted_bits_list.append(str(bit))

        if len(extracted_bits_list) < total_bits_to_extract:
            raise ValueError(
                f"Incomplete encrypted data extracted. "
                f"Got {len(extracted_bits_list)} bits, expected {total_bits_to_extract} bits. "
                f"Image might be corrupted or not contain a full message."
            )

        # Convert extracted bits to bytes
        extracted_encrypted_data_bits = ''.join(extracted_bits_list[:total_bits_to_extract])
        extracted_encrypted_data_bytes = self._to_bytes(extracted_encrypted_data_bits)

        # --- DEBUG PRINTS FOR EXTRACTION ---
        print(f"\n--- EXTRACTION DEBUG ---")
        print(f"Extracted header length: {data_to_extract_len} bytes")
        print(f"Total bits extracted from DCT: {len(extracted_encrypted_data_bits)}")
        print(f"Bytes reconstructed from extracted bits: {len(extracted_encrypted_data_bytes)}")
        # --- END DEBUG PRINTS ---

        # --- DECRYPTION AND DECOMPRESSION ---
        key_bytes = self._derive_key_from_password(password)

        # 3. Decrypt the extracted data
        decrypted_compressed_payload_bytes = AES.decrypt(extracted_encrypted_data_bytes, key_bytes)

        # 4. Decompress the payload
        # This is where 'zlib.error: Error -3' typically occurs if the data is corrupted
        decompressed_json_payload_bytes = zlib.decompress(decrypted_compressed_payload_bytes)

        # 5. Deserialize the JSON payload
        metadata_payload = json.loads(decompressed_json_payload_bytes.decode('utf-8'))

        result = {
            self.METADATA_KEY_TYPE: metadata_payload[self.METADATA_KEY_TYPE],
        }

        # Handle content based on type (now uniformly Base64 decoded)
        if result[self.METADATA_KEY_TYPE] == self.TEXT_TYPE:
            # Decode from base64 and then to UTF-8 string
            result[self.METADATA_KEY_CONTENT] = base64.b64decode(metadata_payload[self.METADATA_KEY_CONTENT]).decode(
                'utf-8')
        elif result[self.METADATA_KEY_TYPE] == self.FILE_TYPE:
            # Decode from base64 to binary bytes
            result[self.METADATA_KEY_CONTENT] = base64.b64decode(metadata_payload[self.METADATA_KEY_CONTENT])
            if self.METADATA_KEY_FILENAME in metadata_payload:
                result[self.METADATA_KEY_FILENAME] = metadata_payload[self.METADATA_KEY_FILENAME]
            if self.METADATA_KEY_FILEEXT in metadata_payload:
                result[self.METADATA_KEY_FILEEXT] = metadata_payload[self.METADATA_KEY_FILEEXT]

        return result

    def _derive_key_from_password(self, password: str) -> bytes:
        """Derives a 32-byte AES key from a string password using SHA256."""
        import hashlib
        return hashlib.sha256(password.encode('utf-8')).digest()

