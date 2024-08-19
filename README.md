#this file implements a encryption with AES- 256bit in mode CTR but whitout uses CTR directly. I use ECB to implement this code.
# I completed all 5 cryptography operation mode for AES and then I used argparse for command-line programming
# by this command can use this in terminal or shell depends on your os 
python file_name.py --mode [encrypt/decrypt] --operation ['cbc','ctr','ofb','cfb','ecb'] -key key_path.file -iv iv_path.file -file plain or cipher_path.file 
