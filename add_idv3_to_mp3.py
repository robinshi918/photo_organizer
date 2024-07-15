import os
from mutagen.easyid3 import EasyID3
import mutagen

def modify_id3_tags(file_path):

    # Extract the file name without extension
    file_name = os.path.splitext(os.path.basename(file_path))[0]
    # Extract the folder name containing the file
    folder_name = os.path.basename(os.path.dirname(file_path))
    print("file(" + str(file_name) + "), folder(" + folder_name +  ")")

    try:
        audio = EasyID3(file_path)
    except mutagen.id3.ID3NoHeaderError:
        audio = mutagen.File(file_path, easy=True)
        audio.add_tags()
    
    # Modify ID3 tags
    audio['title'] = file_name
    audio['artist'] = 'Dora'
    audio['album'] = folder_name
    # audio['genre'] = 'New Genre'
    audio['date'] = '2024'
    
    # Save the changes
    audio.save()
    
    # # Print the changes to verify
    # for key, value in audio.items():
    #     print(f"{key}: {value}")

def traverse_and_modify_mp3s(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.lower().endswith('.mp3'):
                file_path = os.path.join(root, file)
                print(f"Modifying {file_path}")
                modify_id3_tags(file_path)

# Set the directory you want to traverse
directory = '/Users/shiyun/Desktop/modify_mp3/mp3_files'

# Traverse the directory and modify MP3 files
traverse_and_modify_mp3s(directory)
