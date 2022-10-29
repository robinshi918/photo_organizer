"""
export photo from Mac Photo folder

Preparation:
1. connect iPhone with Mac
2. Open Photos app on Mac
3. Go to "Devices", and open the iPhone device
4. cmd+a to select all files, then Import all photos from iPhone to Mac
5. go to "Library"
6. select all files by cmd+a
7. Open "File > Export > Export Unmodified Originals for xxx Items". In the Export dialog, use default options and click "Export" button
8. Select the export target folder
9. Wait until export finishes


method:
1. traverse Mac Photo folder 
2. read create_time tag from exif
       get the time and parse the date time
1. mkdir in target folder
2. copy image to target folder
"""

import os
import datetime
import hashlib
import time
import shutil
import exifread
import re



########################
## CONFIG FLAGS
########################
PRINT_DEBUG = True
DELETE_AFTER_COPY = False
IS_PHOTO = True
ACCEPTED_FILES = ['.jpg', '.jpeg', '.png', '.bmp']
TARGET_BASE_DIR = ""
SRC_DIR = "/Users/robin/Desktop/pixel5_photos_backup"


if IS_PHOTO:
    ACCEPTED_FILES = ['.jpg', '.jpeg', '.png', '.bmp']
    TARGET_BASE_DIR = "/Users/robin/Desktop/pixel5_photos_backup/pixel_Photos"
else:
    ACCEPTED_FILES = ['.mp4', '.mov']
    TARGET_BASE_DIR = "/Users/robin/Desktop/pixel5_photos_backup/pixel_Videos"

TOTAL_FILE_NUM = 0
CURRENT_PROGRESS = 0

def log(text):
    """
    log method
    """
    if PRINT_DEBUG:
        print(text)

def get_file_modification_time(file_path):
    """
    get modification time of file
    """
    timestamp = os.path.getmtime(file_path)
    time_string = datetime.datetime.fromtimestamp(
        int(os.path.getmtime(file_path))
        ).strftime('%Y:%m:%d %H')
    return time_string


#'VID_20191123_180729.mp4'
def get_timestamp_from_mp4(file_name):
    pattern = 'VID_\d{8}_\d{6}.mp4'
    result = re.match(pattern, file_name)

    if result:
        parts = file_name.split('.')[0].split('_')
        print(parts)
        _date = parts[1]
        _time = parts[2]
        
        print("date = " + str(_date))
        print("time = " + str(_time))
        y = _date[0:4]
        month = _date[4:6]
        d = _date[6:8]        

        h = _time[0:2]
        minute = _time[2:4]
        s = _time[4:6]

        #2013:11:16 17:44:16
        return y + ':' + month + ':' + d + ' ' + h + ':' + minute + ':' + s
    else:
        return ""


def read_photo_date(file_name):
    """
    read the file and return the year, month, day tuple
    """
    # Open image file for reading (binary mode)
    fd = open(file_name, 'rb')

    # Return Exif tags
    tags = exifread.process_file(fd)
    try:
        date_time = tags['EXIF DateTimeOriginal']
    except KeyError:
        date_time  = get_timestamp_from_mp4(os.path.basename(file_name))
        if date_time == "":
            # date time info is not valid in exif, try to get file's create time
            date_time = get_file_modification_time(file_name)

    log(str(date_time) + "--->" + str(file_name))

    #parse date time string and returns tuple
    words = str(date_time).split(' ')[0].split(':')  #2013:11:16 17:44:16
    if len(words) == 3:
        y = words[0]
        m = words[1]
        d = words[2]
    else:
        words = str(date_time).split(' ')[0].split('-')  # 2015-01-08 16:05:13
        y = words[0]
        m = words[1]
        d = words[2]

    #returns a tuple
    return y, m, d

def mkdir(directory):
    """
    create a folder if not exist
    """
    if not os.path.exists(directory):
        os.makedirs(directory)


def scan_folder(base_folder):
    """
    main entry to the tool, traverse the directory tree,
    """
    start_time = time.time()
    for dirpaths, dirnames, filenames in os.walk(base_folder):
        for fname in filenames:
            if is_accept_type(fname):
                src_file_path = os.path.join(dirpaths, fname)
                year, month, day = read_photo_date(src_file_path)
                target_folder = os.path.join(TARGET_BASE_DIR, str(year) + '_' + str(month) + '/')
                copy(src_file_path, target_folder, fname)
    time_elapsed = time.time() - start_time
    print(str(time_elapsed) + " seconds used")

def is_accept_type(file_name):
    """
    check if the file type is valid extension
    """
    bare_name, file_extension = os.path.splitext(file_name)
    for ext in ACCEPTED_FILES:
        if file_extension.lower() == ext:
            return True
    return False


def md5(file_path):
    return hashlib.md5(open(file_path, 'rb').read()).hexdigest()

def copy(src_file_name, target_folder, file_name):
    """
    copy src_file_name to target_folder.
    1. target_folder will be created if not exists
    2. if same file name already exists in target folder
        a. if file md5 is same, skip
        b. if file md5 is different, copy to a new file
    """

    global CURRENT_PROGRESS
    global TOTAL_FILE_NUM
    CURRENT_PROGRESS += 1

    mkdir(target_folder)
    target_file = os.path.join(target_folder, file_name)

    if os.path.exists(target_file):
        src_md5 = md5(src_file_name)

        # iterate target folder to check if file already exists
        for file_in_target in os.listdir(target_folder):
            entry = os.path.join(target_folder, file_in_target)
            target_md5 = md5(entry)
            if src_md5 == target_md5:
                log("(" + str(CURRENT_PROGRESS) + "/" + str(TOTAL_FILE_NUM) + file_name + "file exists, ignore COPY. <-- " + src_file_name)
                return

        word_list = file_name.split('.')
        num_of_files = len(
            [f for f in os.listdir(target_folder) \
                if os.path.isfile(os.path.join(target_folder, f))])
        file_name = word_list[0] + '(' + str(num_of_files) + ').' + word_list[1]
        target_file = os.path.join(target_folder, file_name)

    if DELETE_AFTER_COPY:
        log("(" + str(CURRENT_PROGRESS) + '/' + str(TOTAL_FILE_NUM) + ")MOVE: " + src_file_name + " --->" + target_file)
        shutil.move(src_file_name, target_file)
    else:
        log("(" + str(CURRENT_PROGRESS) + '/' + str(TOTAL_FILE_NUM) + ")COPY: " + src_file_name + " --->" + target_file)
        shutil.copy(src_file_name, target_file)

def get_file_size(file_path):
    """
    get file size in bytes
    """
    return os.path.getsize(file_path)


def initialize():
    print("Initializing......")
    total_size = 0
    start_time = time.time()
    global TOTAL_FILE_NUM
    for dirpaths, dirnames, filenames in os.walk(SRC_DIR):
        for fname in filenames:
            if is_accept_type(fname):
                TOTAL_FILE_NUM = TOTAL_FILE_NUM + 1
                total_size += os.path.getsize(os.path.join(dirpaths, fname))
    time_ellapsed = time.time() - start_time
    print ("initialization Done! " + str(TOTAL_FILE_NUM) + " files to export(" + str(total_size) + " Bytes) - (" + str(time_ellapsed) +" seconds)")

initialize()
scan_folder(SRC_DIR)

print ("END")




   
