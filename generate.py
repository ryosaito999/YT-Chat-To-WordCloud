import numpy as np
import pandas as pd
from os import path, replace
from PIL import Image
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
from wordcloud import STOPWORDS

import matplotlib.pyplot as plt
from chat_downloader import ChatDownloader

import re
import os
import json
import sys
import time

def get_abs_path(path):
    return os.path.abspath(os.path.expanduser(os.path.expandvars(path)))

def get_yt_vid_id(url):
    if(len(url) <= 0):
        return ""
    
    m = re.search(r'\?v=(.*$)', url)
    if m:
        return m.group(1)
    return ""

url = 'https://www.youtube.com/watch?v=kYChcl_6rvs'
try:
    chat = ChatDownloader().get_chat(url)       
except Exception as e:
    print("Could not get chat for URL, exiting...")
    exit(-1)

word_cloud_string = ""
vid_id = get_yt_vid_id(url)
if not os.path.exists(vid_id):

    chat_log = open(vid_id, 'w', encoding="utf-8", errors="ignore")
    print("Backing up chat log in %s" % (get_abs_path(vid_id)))
    i = 0

    for json_message in chat:                            
        text_msg = json_message['message']
        time_stamp = json_message['time_text']
        text_msg = re.sub(r':.*?:', '', text_msg)

        chat_log.write(text_msg + "\n")
        if(len(text_msg.strip()) >0):
            word_cloud_string += text_msg + "\n"

        progress_msg = '\rMessages Processed: %d Video Time: %s' %(i, time_stamp)
        sys.stdout.write(progress_msg)
        sys.stdout.flush()
        i += 1
else:
    chat_log = open(vid_id, 'r', encoding='utf-8')
    for line in chat_log:
        word_cloud_string += (line + '\n')

mask = np.array(Image.open("gura.png"))
image_colors = ImageColorGenerator(mask)
font_path="/home/ryota/Documents/noto_sans/NotoSansCJKjp-Light.otf"

wc = WordCloud(background_color='black',stopwords=STOPWORDS, collocations=False,
max_font_size=512, min_font_size=10, max_words=4000, 
relative_scaling=0.5, mask=mask, random_state=3, scale=5, 
width=4000, height=4000, font_path=font_path);

wc.generate(word_cloud_string)
plt.axis('off')
plt.figure( figsize=(40,40) )

plt.tight_layout(pad=0)
plt.imshow(wc.recolor(color_func=image_colors), interpolation="bilinear")
plt.axis('off')
plt.savefig("gura_wc.png", format="png", dpi=300, facecolor='k', bbox_inches='tight')



