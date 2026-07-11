from utility.helper import *
from utility.scraper import parse_html_cna, parse_html_gn, parse_html_nhk
from utility.formatter import format_markdown

# States
NODE, CNA, GRND, NHK = range(4)

# Number of hours before .json for news needs to be updated
hours = 6

# Boilerplate message
return_message = "Returned to news node"

# -------------------------------------------------- #
# Main node                                          #
# -------------------------------------------------- #

async def news_node(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    name, username = user["first_name"], user["username"]
    print(f"\n>> news.py > news_node > User: {username}")
    message = "\n".join([f"- news node -", "/cna", "/grnd", "/nhk"])
    await update.message.reply_text(message)
    return NODE

# -------------------------------------------------- #
# Channel News Asia                                  #
# -------------------------------------------------- #

async def news_cna(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Fetching articles from Channel News Asia...")

    global cna_json_path
    to_update_cna, cna_json_path = check_file_update(file = cna_json, folder_path = json_folder_path, hours = hours)
    
    if to_update_cna:
        await parse_html_cna()
    else:
        print(f"> '{cna_json}' last modified < {hours} hours ago, skipping scraping")

    with open(cna_json_path, 'r') as file:
        news_dict = json.load(file)
        if news_dict:
            SORT_ORDER = {"Business": 0, "World": 1, "Singapore": 2, "Asia": 3, "East Asia": 4}
            message = "Select news category"
            reply_keyboard = list(news_dict.keys())
            reply_keyboard.sort(key = lambda val : SORT_ORDER[val])
            reply_keyboard = [reply_keyboard]
            await update.message.reply_text(message, reply_markup = ReplyKeyboardMarkup(keyboard = reply_keyboard, resize_keyboard = False, one_time_keyboard = False, input_field_placeholder = "Select category"))
            return CNA
        else:
            await update.message.reply_text("failed")
            await update.message.reply_text(return_message)
            return NODE

async def show_cna(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:    
    topic = update.message.text
    last_modified = datetime.datetime.fromtimestamp(os.path.getmtime(cna_json_path)).strftime("%Y-%m-%d, %H:%M")
    message = f"CNA・{topic}\nLast fetched {format_markdown(last_modified)}\n"
    with open(cna_json_path, 'r') as file:
        news_dict = json.load(file)
    count = 0
    for article in news_dict[topic]:
        # Limit number of articles to show
        if count < 15:
            title, link = format_markdown(article[0]), format_markdown(article[1])
            message += f"> [{title}]({link})\n\n"
            count += 1
        else:
            break
    await update.message.reply_markdown_v2(message)

# -------------------------------------------------- #
# Ground News                                        #
# -------------------------------------------------- #

async def news_gn(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Fetching articles from Ground News...")

    global gn_json_path
    to_update_gn, gn_json_path = check_file_update(file = gn_json, folder_path = json_folder_path, hours = hours)

    # Run scraper if .json file does not exist or needs to be updated
    if to_update_gn:
        await parse_html_gn()
    else:
        print(f"> '{gn_json}' last modified < {hours} hours ago, skipping scraping")

    with open(gn_json_path, 'r') as file:
        news_dict = json.load(file)
        if news_dict:
            message = "Select news category"
            reply_keyboard = list(news_dict.keys())
            reply_keyboard = [reply_keyboard]
            await update.message.reply_text(message, reply_markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard = False, one_time_keyboard = False, input_field_placeholder = "Select category"))
            return GRND
        else:
            await update.message.reply_text("failed")
            await update.message.reply_text(return_message)
            return NODE
  
async def show_gn(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    topic = update.message.text
    last_modified = datetime.datetime.fromtimestamp(os.path.getmtime(gn_json_path)).strftime("%Y-%m-%d, %H:%M")
    message = f"Ground News・{topic}\nLast fetched {format_markdown(last_modified)}\n"
    with open(gn_json_path, 'r') as file:
        news_dict = json.load(file)
    count = 0
    for article in news_dict[topic]:
        # Limit number of articles to show
        if count < 15:
            title, link = format_markdown(article[0]), format_markdown(article[1])
            message += f"> [{title}]({link})\n\n"
            count += 1
        else:
            break
    await update.message.reply_markdown_v2(message)

# -------------------------------------------------- #
# NHK Japan                                          #
# -------------------------------------------------- #

async def news_nhk(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Fetching articles from NHK Japan...")

    global nhk_json_path
    to_update_nhk, nhk_json_path = check_file_update(file = nhk_json, folder_path = json_folder_path, hours = hours)

    if to_update_nhk:
        await parse_html_nhk()
    else:
        print(f"> '{nhk_json}' last modified < {hours} hours ago, skipping scraping")

    with open(nhk_json_path, 'r') as file:
        news_dict = json.load(file)
        if news_dict:
            message = "Select news category"
            reply_keyboard = list(news_dict.keys())
            reply_keyboard = [reply_keyboard]
            await update.message.reply_text(message, reply_markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard = False, one_time_keyboard = False, input_field_placeholder = "Select category"))
            return NHK
        else:
            await update.message.reply_text("failed")
            await update.message.reply_text(return_message)
            return NODE
        
async def show_nhk(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:    
    topic = update.message.text
    last_modified = datetime.datetime.fromtimestamp(os.path.getmtime(nhk_json_path)).strftime("%Y-%m-%d, %H:%M")
    message = f"NHK Japan・{topic}\nLast fetched {format_markdown(last_modified)}\n"
    with open(nhk_json_path, 'r') as file:
        news_dict = json.load(file)
    count = 0
    for article in news_dict[topic]:
        # Limit number of articles to show
        if count < 15:
            title, link = format_markdown(article[0]), format_markdown(article[1])
            message += f"> [{title}]({link})\n\n"
            count += 1
        else:
            break
    await update.message.reply_markdown_v2(message)