# Import libraries
from http import client
from datetime import datetime
import requests
import time
import os

# Check cctv image folder exist or not
cctv_image_save_dir = 'cctv_images/'
if not os.path.isdir(cctv_image_save_dir):
    os.mkdir(cctv_image_save_dir)

# Use HTTP Protocal Version 1.0
client.HTTPConnection._http_vsn = 10
client.HTTPConnection._http_vsn_str = 'HTTP/1.0'

# HTTP request setting
url = 'http://cctvn01.freeway.gov.tw/vStream.php?pm=160,A40,13' # CCTV URL
headers = {'User-Agent': 'User-Agent:Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'}

# Image filename string
current_datetime = datetime.now()
datetime_string = current_datetime.strftime('%Y%m%d_%H%M%S')

# Send request
r = requests.get(url, headers=headers)
print('request done!')

# Check return status
if r.status_code == requests.codes.ok:

    content = r.content # Get request content in byte form

    jfif_flag = b'\xff\xd8\xff\xe0\x00\x10\x4a\x46\x49\x46' # JFIF start string
    content_list = content.split(jfif_flag) # Split with jfif start flag
    content_list = content_list[1:] # discard first element
    print('Total image amount = ', len(content_list))

    # Save image file
    os.mkdir(os.path.join(cctv_image_save_dir, datetime_string)) # Create new folder with current datetime
    for i, content in enumerate(content_list):

        raw_image = jfif_flag + content # Add jfif start flag
        image_filepath = '%s/%s/%s.jpg' % (cctv_image_save_dir, datetime_string, str(i)) # Set new image filename
        # Save
        with open(image_filepath, 'wb') as f:
            f.write(raw_image)
