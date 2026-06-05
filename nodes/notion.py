from utility.helper import *

# States
NOTIONMENU, JP_VOCAB_GET, JP_VOCAB_ANS, JP_VOCAB_UPD = range(4)
reply_keyboard = [["☓", "◯"]]

# -------------------------------------------------- #
# Main node                                          #
# -------------------------------------------------- #

async def notion_node(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    name, username = user["first_name"], user["username"]
    print(f"\n>> notion.py > notion_node > User: {username}")
    if username == master:
        message = "\n".join(["- notion node -",
                            "/jpvocab - 日本語の語彙を練習"
                            # "/command - do something on Notion",
                            # "/command - do something on Notion",
                            ])
    else:
        message = f"Hey '{name}' you can't access this node!"
    await update.message.reply_text(message)
    return NOTIONMENU

# -------------------------------------------------- #
# 語彙の練習                                           #
# -------------------------------------------------- #

async def notion_jpvocab(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = "語彙の練習：１から３０までの数字を入力してください"
    await update.message.reply_text(message, reply_markup=ReplyKeyboardRemove())
    return JP_VOCAB_GET


async def notion_jpvocab_get(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global page_size; page_size = update.message.text
    page_size = int(page_size)
    message = f"Fetching {page_size} entries..."
    await update.message.reply_text(message)
    payload = {
        "sorts": [ 
            {
                "property": "revised", "direction": "ascending"
            }
        ],
        "filter": {
            "property": "state", "type": "select",
            "select": { "equals": "redo" }
        },
        "page_size": page_size,
        "in_trash": False,
        "result_type": "page"
    }
    success = post_querydatasource(data_source_id = notion_datasource_id_jpvocab, payload = payload)
    if success:
        await update.message.reply_text("ok")
        global curr; curr = 0
        with open(json_folder_path + "/" + notion_jpvocab_json, 'r') as file:
            global vocab_dict
            vocab_dict = json.load(file)
        global pages_to_update; pages_to_update = defaultdict()
        message = "Press Start to commence practice"
        await update.message.reply_text(message, reply_markup=ReplyKeyboardMarkup([["Start"]], resize_keyboard=True, one_time_keyboard=False))
        return JP_VOCAB_ANS
    else:
        message = "Failed, returned to Notion menu"
        await update.message.reply_text(message)
        return NOTIONMENU


async def notion_jpvocab_ans(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global curr
    vocab = vocab_dict[curr]
    vocabID = vocab["id"]
    properties   = vocab["properties"]
    vocabName    = properties["name"]["title"][0]["text"]["content"]
    # vocabRevised = properties["Revised"]["date"]["start"]
    message = f"Vocab {curr+1} / {page_size} >>> {vocabName}"
    await update.message.reply_text(message, reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=False))

    state_value = "ok" if update.message.text == "◯" else "redo"
    pages_to_update[vocabID] = state_value
    curr += 1

    if curr < page_size:
        return JP_VOCAB_ANS
    else:
        return JP_VOCAB_UPD


async def notion_jpvocab_update(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f">> notion.py > notion_jpvocab_update")
    message = "Practice ended, updating vocab database..."
    await update.message.reply_text(message, reply_markup = ReplyKeyboardRemove())
    revised_value = datetime.now().strftime("%Y-%m-%d")
    successful_updates = 0
    for page_id, state_value in pages_to_update.items():
        payload = {
            "properties": {
                "state": {
                    "type": "select",
                    "select": { "name": state_value }
                },
                "revised": {
                    "date": { "start": revised_value },
                    "type": "date"
                }
            }
        }
        success = patch_updatepage(page_id = page_id, payload = payload)
        successful_updates += 1 if success else 0
    if successful_updates == page_size:
        message = "Update successful"
    elif successful_updates > 1:
        message = f"Update was partially successful, {successful_updates}/{page_size} notion pages were updated"
    else:
        message = "Update failed, no pages were updated"
    print(f"> Updated {successful_updates}/{page_size} notion pages")
    await update.message.reply_text(message)
    message = "Returning to Notion menu..."
    await update.message.reply_text(message)
    return NOTIONMENU

# -------------------------------------------------- #
# API functions                                      #
# -------------------------------------------------- #

def post_querydatasource(data_source_id, payload):
    print(">> notion.py > post_querydatasource (POST) > ", end = "")
    url = f"https://api.notion.com/v1/data_sources/{data_source_id}/query"
    pages = []    
    response = requests.post(url, json = payload, headers = notion_headers)
    if response:
        data = response.json()
        pages.extend(data.get("results", []))
        with open(json_folder_path + "/" + notion_jpvocab_json, 'w') as file:
            json.dump(pages, file, indent=4)
        print("ok")
        return True
    else:
        print("failed")
        return False


def patch_updatepage(page_id, payload):
    print(">> notion.py > patch_updatepage (PATCH) > ", end = "")
    url = f"https://api.notion.com/v1/pages/{page_id}"
    response = requests.patch(url, json = payload, headers = notion_headers)
    if response:
        print("ok")
        return True
    else:
        print("failed")
        return False
