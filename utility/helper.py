# -------------------------------------------------- #
# imports                                            #
# -------------------------------------------------- #

from bs4 import BeautifulSoup
from collections import defaultdict
from datetime import date, timedelta
from dotenv import load_dotenv # dotenv_values
from google import genai
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import Application, CommandHandler, ConversationHandler, ContextTypes, MessageHandler, filters
import aiohttp, asyncio, datetime, sys, os, json, requests
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.animation as animation
import numpy as np

# -------------------------------------------------- #
# directory functions                                #
# -------------------------------------------------- #

def initialise_data_folder():
    print(f">>> helper.py > initialise_data_folder")

    curr_dir = os.getcwd()
    data_folder = "_data"
    # print(f">> helper.py > Current directory: '{curr_dir}'")
    data_folder_path = curr_dir + "/" + data_folder

    for root, dirs, files in os.walk(curr_dir):
        if data_folder in dirs:
            print(f"> Folder '{data_folder}' found in '{curr_dir}'")
            return data_folder_path
        # print(f"> {root} | {dirs} | {files}")
        break # Only searching for target folder within current directory
    
    print(f"> Folder '{data_folder}' not found in '{curr_dir}' > Creating new data folders...")
    try:
        os.mkdir(data_folder)
        os.mkdir(data_folder + "/_html")
        os.mkdir(data_folder + "/_json")
        print(f"> Created data folder '{data_folder}' and child folders '_html' and '_json'")
    except PermissionError:
        print(f"> Permission denied: Unable to create new data folders")
    except Exception as e:
        print(f"> An error occurred: {e}")
    
    return data_folder_path

# Checks if file exists, if no > creates a new blank file
# Returns the file path

def check_file(file: str, folder_path: str):
    print(f">>> helper.py > check_file")

    file_path = folder_path + "/" + file
    if os.path.exists(file_path):
        print(f"> Found '{file}' in '{folder_path}'")
    else:
        with open(file_path, "w") as new_file:
            pass
        print(f"> '{file}' not found in '{folder_path}' > Created new blank file")
    return file_path

# Checks if file exists
# If yes > check if last modified more than specified number of hours ago
# If no > create a new blank file
# Returns boolean value - True = file needs to be created/updated
# Also returns its file path

def check_file_update(file: str, folder_path: str, hours: int):
    print(f">>> helper.py > check_file_update")

    file_path = folder_path + "/" + file
    to_update = True
    if os.path.exists(file_path):
        last_modified = datetime.datetime.fromtimestamp(os.path.getmtime(file_path))
        hours_ago = (datetime.datetime.now() - last_modified).days * 24 + (datetime.datetime.now() - last_modified).seconds / 3600
        if hours_ago <= hours:
            to_update = False
        print(f"> Found '{file}', last modified {round(hours_ago, 0)} hours ago")
    else:
        with open(file_path, "w") as new_file:
            pass
        print(f"File '{file}' not found in '{folder_path}'> Created new blank file")
        to_update = True
    return to_update, file_path

# -------------------------------------------------- #
# data folder paths                                  #
# -------------------------------------------------- #

data_path = initialise_data_folder()
html_folder_path = data_path + "/" + "_html"
json_folder_path = data_path + "/" + "_json"

# -------------------------------------------------- #
# .env variables                                     #
# -------------------------------------------------- #

load_dotenv()
master = os.getenv("MASTER")
telegram_token = os.getenv("TELEGRAM_API_TOKEN")
notion_token_workspace_1 = os.getenv("NOTION_API_TOKEN_AKR")
notion_datasource_id_jpvocab = os.getenv("NOTION_AKR_DATASOURCE_ID_NIHONGONOGOI")
# notion_datasource_id_ = os.getenv("NOTION_AKR_DATASOURCE_ID_")
steam_token = os.getenv("STEAM_API_TOKEN")
steam_id = os.getenv("STEAM_ID")
gemini_token = os.getenv("GEMINI_API_TOKEN")

# -------------------------------------------------- #
# standard.py > get_time()                           #
# -------------------------------------------------- #

weekdays_en_jp = {"Monday"   : "月",
                  "Tuesday"  : "火",
                  "Wednesday": "水",
                  "Thursday" : "木",
                  "Friday"   : "金",
                  "Saturday" : "土",
                  "Sunday"   : "日"}

# -------------------------------------------------- #
# data folder > file variables                       #
# -------------------------------------------------- #

bedtime_log   = "bedtime_log.txt"
expense_log = "expense_log.txt"

bedtime_plot_png = "bedtime_plot.png"
bedtime_plot_gif = "bedtime_plot.gif"

cna_html = "news_cna.html"
cna_json = "news_cna.json"
gn_json = "news_gn.json"
nhk_json = "news_nhk.json"

notion_jpvocab_json = "notion_jpvocab.json"

steam_json_1 = "steam_recentlyplayedgames.json"
steam_json_2 = "steam_wishlist.json"

# -------------------------------------------------- #
# news.py                                            #
# -------------------------------------------------- #

# CNA
cna_url = "https://www.channelnewsasia.com/"
cna_topics   = {"business": "Business",
                "world": "World",
                "east-asia": "East Asia",
                "asia": "Asia",
                "singapore": "Singapore"}

# Ground News
gn_url  = "https://ground.news/interest/"
gn_base = "https://ground.news"
gn_topics = {"stock-markets": "Stock Markets", 
             "tech": "Tech", 
             "asia": "Asia", 
             "north-america": "North America"}

# NHK Japan
nhk_url = "https://news.web.nhk/newsweb/genre/"
nhk_topics   = {"business"     : "経済", 
                "society"      : "社会", 
                "politics"     : "政治", 
                "international": "国際"}

# -------------------------------------------------- #
# api variables                                      #
# -------------------------------------------------- #

notion_version = "2026-03-11"
notion_headers = {'Authorization': f"Bearer {notion_token_workspace_1}",
                  'Content-Type': 'application/json',
                  'Notion-Version': notion_version}

# -------------------------------------------------- #
# prompt instructions for large language models      #
# -------------------------------------------------- #
gemini_model = "gemini-3-flash-preview"

SEARCH_INSTRUCTIONS = '''Strictly adhere to the following rules when answering the prompt:
                    - Search for sources from your knowledge database that answers the prompt, such as links to websites or books
                    - Then, return the sources used
                    Prompt: 
                    '''

CHECK_INSTRUCTIONS = '''Strictly adhere to the following rules when answering the prompt:
                    - Cross-check the prompt with sources in your knowledge database
                    - Provide a short paragraph of the answer to the prompt
                    - Then, return the list of sources used in your knowledge database to answer the prompt
                    Prompt: 
                    '''