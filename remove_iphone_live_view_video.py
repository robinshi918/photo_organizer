
import os
import datetime
import hashlib
import time
import shutil
import exifread
import re
import datetime

"""
remove mov files when below 2 conditions are met:
1. Two files have same name but different extension(mov vs. jpeg)
2. two files have close shot date, time gap is smaller than 1 day
"""

# def md5(file_path):
#     return hashlib.md5(open(file_path, 'rb').read()).hexdigest()

# def is_same_file(file1, file2):
#     if os.path.exists(file1) and os.path.exists(file2):
#         return md5(file1) == md5(file2)
#     return False


def mkdir(directory):
    """
    create a folder if not exist
    """
    if not os.path.exists(directory):
        os.makedirs(directory)

base_folder = "/Users/robinshi/Desktop/iphone_export"
rubbish_bin = "/Users/robinshi/Desktop/photo_organizer/live_view_videos"

def throw_to_rubbish(path):
    print("deleting " + path)
    mkdir(rubbish_bin)
    shutil.move(path, rubbish_bin)

def get_file_modification_time(file_path):
    """
    get modification time of file
    """
    timestamp = os.path.getmtime(file_path)
    time_string = datetime.datetime.fromtimestamp(
        int(os.path.getmtime(file_path))
        ).strftime('%Y-%m-%d %H:%M:%S')
    return time_string

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
        date_time = get_file_modification_time(file_name)
        # date time info is not valid in exif, try to get file's create time

    #parse date time string and returns tuple
    words = str(date_time).split(' ')[0].split(':')  #2013:11:16 17:44:16
    if len(words) == 3:
        result = datetime.datetime.strptime(str(date_time), '%Y:%m:%d %H:%M:%S')
    else:
        result = datetime.datetime.strptime(str(date_time), '%Y-%m-%d %H:%M:%S')
    return result
        

def is_in_same_day(datetime1, datetime2):
    return abs((datetime1 - datetime2).total_seconds()) < (60 * 60 * 24)

counter = 1
for dirpaths, dirnames, filenames in os.walk(base_folder):
    for fname in filenames:
        
        if fname.endswith(".mov"):
            name_without_ext = re.sub(".mov", "", fname)
            jpeg_name = name_without_ext + ".jpeg"

            mov_full_path = os.path.join(dirpaths, fname)
            jpeg_full_path = os.path.join(dirpaths, jpeg_name)

            if os.path.exists(jpeg_full_path):
                mov_datetime = read_photo_date(mov_full_path)
                jpg_datetime = read_photo_date(jpeg_full_path)
                
                counter += 1
                
                if is_in_same_day(mov_datetime, jpg_datetime):
                    # print("[" + str(counter) +"]deleting " + mov_full_path)
                    throw_to_rubbish(mov_full_path)
                    
                


