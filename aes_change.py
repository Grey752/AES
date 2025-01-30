from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.core.text import LabelBase
from kivy.resources import resource_add_path
import base64
import random
import string
import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from kivy.core.clipboard import Clipboard

class AESCryptoApp(App):
    def build(self):
        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Input text box
        self.input_text = TextInput(multiline=True, hint_text='Enter text to encrypt/decrypt')
        self.layout.add_widget(self.input_text)
        
        # Encrypt/Decrypt buttons
        btn_layout = BoxLayout(size_hint_y=None, height=40, spacing=10)
        self.encrypt_btn = Button(text='Encrypt')
        self.encrypt_btn.bind(on_press=self.encrypt)
        self.decrypt_btn = Button(text='Decrypt')
        self.decrypt_btn.bind(on_press=self.decrypt)
        btn_layout.add_widget(self.encrypt_btn)
        btn_layout.add_widget(self.decrypt_btn)
        self.layout.add_widget(btn_layout)
        
        # Output text box
        self.output_text = TextInput(multiline=True, readonly=True)
        self.layout.add_widget(self.output_text)
        
        # Copy button
        self.copy_btn = Button(text='Copy Result', size_hint_y=None, height=40)
        self.copy_btn.bind(on_press=self.copy_output)
        self.layout.add_widget(self.copy_btn)
        
        return self.layout

    def copy_output(self, instance):
        Clipboard.copy(self.output_text.text)

    def generate_key(self):
        # Generate random 16 byte key
        return os.urandom(16)
        
    def encrypt(self, instance):
        try:
            # Get plaintext
            plaintext = self.input_text.text.encode()
            
            # Generate random key and IV
            key = self.generate_key()
            iv = os.urandom(16)
            
            # Use AES-CBC mode for encryption
            cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
            encryptor = cipher.encryptor()
            
            # PKCS7 padding
            pad_len = 16 - (len(plaintext) % 16)
            plaintext += bytes([pad_len]) * pad_len
            
            # Encrypt
            ciphertext = encryptor.update(plaintext) + encryptor.finalize()
            
            # 将key和iv直接拼接到密文前面
            final_data = base64.b64encode(key + iv + ciphertext)
            
            self.output_text.text = final_data.decode()
            
        except Exception as e:
            self.output_text.text = f"Encryption error: {str(e)}"

    def decrypt(self, instance):
        try:
            # Get ciphertext
            data = base64.b64decode(self.input_text.text.encode())
            
            # 从密文中提取key、iv和实际密文
            key = data[:16]
            iv = data[16:32]
            ciphertext = data[32:]
            
            # Decrypt
            cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
            decryptor = cipher.decryptor()
            plaintext = decryptor.update(ciphertext) + decryptor.finalize()
            
            # Remove padding
            pad_len = plaintext[-1]
            plaintext = plaintext[:-pad_len]
            
            self.output_text.text = plaintext.decode()
            
        except Exception as e:
            self.output_text.text = f"Decryption error: {str(e)}"

if __name__ == '__main__':
    AESCryptoApp().run()
