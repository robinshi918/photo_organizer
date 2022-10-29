
import os
import datetime
import hashlib
import time
import shutil
import exifread
import re

def md5(file_path):
    return hashlib.md5(open(file_path, 'rb').read()).hexdigest()

def is_same_file(file1, file2):
    if os.path.exists(file1) and os.path.exists(file2):
        return md5(file1) == md5(file2)
    return False

def is_file_suspicious(file_name):
    x = re.search(" *\(\d+\)", file_name)
    return x != None

def rip_suspicious_file(file_name):
    return re.sub(" *\(\d+\)", "", file_name)
 
def mkdir(directory):
    """
    create a folder if not exist
    """
    if not os.path.exists(directory):
        os.makedirs(directory)

base_folder = "/Users/robin/Desktop/iPhone_export"
rubbish_bin = "/Users/robin/Desktop/photo_organizer/rubbish_bin"

def throw_to_rubbish(path):
    print("deleting " + path)
    mkdir(rubbish_bin)
    shutil.move(path, rubbish_bin)
    

for dirpaths, dirnames, filenames in os.walk(base_folder):
    for fname in filenames:
        full_path = os.path.join(dirpaths, fname)
        if is_file_suspicious(fname): 
            authentic_file_path = os.path.join(dirpaths, rip_suspicious_file(fname))
            if is_same_file(authentic_file_path, full_path):
                throw_to_rubbish(full_path)

