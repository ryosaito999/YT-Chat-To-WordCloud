#!/usr/bin/env python3
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
import configparser
from optparse import OptionParser

class CustomError(Exception): 
    def __init__(self, value): 
        self.value = value
    def __str__(self): 
        return "Error: %s" % self.value

def get_project_dir():
    return os.path.dirname(__file__)

def get_abs_path(path):
    return os.path.abspath(os.path.expanduser(os.path.expandvars(path)))

def get_yt_vid_id(url):
    if(len(url) <= 0):
        return ""
    
    m = re.search(r'\?v=(.*$)', url)
    if m:
        return m.group(1)
    return ""

def setup_wordcloud(config_path, font_path, mask):

    #Read config.ini for word cloud settings 
    config = configparser.ConfigParser()
    config.read(config_path)
    if 'WORDCLOUD_SETTINGS' not in config:
        raise CustomError("Missing WORDCLOUD_SETTINGS block in config.ini")

    wc_setting = config['WORDCLOUD_SETTINGS']
    background_color = wc_setting.get('background_color', 'black')
    width = wc_setting.get('width', 4000)
    height = wc_setting.get('height', 4000)
    scale = wc_setting.get('scale', 5)
    max_words = wc_setting.get('max_words', 4000)
    min_font_sz = wc_setting.get('min_font_size', 10)
    max_font_sz = wc_setting.get('max_font_size', 512)
    collocations = wc_setting.get('collocations', False)
    relative_scaling=wc_setting.get('relative_scaling', 0.5)

    wc = WordCloud(
    background_color=background_color,
    stopwords=STOPWORDS, 
    font_path=font_path,
    collocations=bool(collocations),
    max_font_size=int(max_font_sz), 
    min_font_size=int(min_font_sz), 
    max_words=int(max_words), 
    relative_scaling=float(relative_scaling), 
    mask=mask, 
    random_state=3, 
    scale=int(scale), 
    width=int(width), 
    height=int(height)
    );

    return wc

image_path=""
chat_log_path=""
output_path=""

usage = "usage: %prog <URL> [options]"
parser = OptionParser(usage)
parser.add_option("-i", "--image",
                  help="word cloud mask image file", 
                  metavar="FILE", action="store", type="string", dest="image_path")
parser.add_option("-c", "--chatlog", 
                  help="use youtube chat log archive file intstead", 
                  metavar="FILE", action="store", type="string", dest="chat_log_path")
parser.add_option("-o", "--output",
                  help="name custom output path for wordcloud",
                  metavar="FILE", action="store", type="string", dest="output_path")

(options, args) = parser.parse_args()
if len(args) != 1:
    parser.error("Missing URL")

CONFIG_PATH = get_project_dir() + "/config.ini"
font_path = get_project_dir() + "/NotoSansCJKjp-Light.otf"

try:
    mask = np.array(Image.open("gura.png"))
except FileNotFoundError:
    print("Could not find word cloud mask image")
    exit(-1)

wc = setup_wordcloud(CONFIG_PATH, font_path, mask)
image_colors = ImageColorGenerator(mask)

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


print ("Generating Word Cloud...")
wc.generate(word_cloud_string)
plt.axis('off')
plt.figure(figsize=(40,40))
plt.tight_layout(pad=0)
plt.imshow(wc.recolor(color_func=image_colors), interpolation="bilinear")
plt.axis('off')
plt.savefig("word_cloud.png", format="png", dpi=300, facecolor='k', bbox_inches='tight')
print ("Created word_cloud.png within current directory. Exiting...")



