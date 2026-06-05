from utility.helper import *

# States
LLM_MENU, QUERY_TYPE, INPUT_PROMPT = range(3)

# Keyboard reply
reply_keyboard_type = [["search", "summarise", "check", "free"]]

# Prompt Type to Instructions map
prompt_instructions = {"search": SEARCH_INSTRUCTIONS,
                       "summarise": SUMMARY_INSTRUCTIONS,
                       "check": CHECK_INSTRUCTIONS}

# -------------------------------------------------- #
# Main node                                          #
# -------------------------------------------------- #

async def gemini_node(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    name, username = user["first_name"], user["username"]
    print(f"\n>> gemini.py > gemini_node > User: {username}")
    message = "\n".join(["- gemini node -",
                        "Choose prompt type"
                        ])
    await update.message.reply_text(message, reply_markup = ReplyKeyboardMarkup(reply_keyboard_type, resize_keyboard = True, one_time_keyboard = False))
    return LLM_MENU

# -------------------------------------------------- #
# Prompt functions                                   #
# -------------------------------------------------- #

async def gemini_input_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    global prompt_type
    prompt_type = update.message.text
    message = "Input your prompt"
    await update.message.reply_text(message, reply_markup = ReplyKeyboardRemove())
    return INPUT_PROMPT

async def gemini_answer_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    prompt_input = update.message.text
    message = "Sending prompt to Google Gemini..."
    await update.message.reply_text(message)
    output = gemini_send_prompt(prompt_type = prompt_type, prompt_input = prompt_input)
    if output:
        await update.message.reply_text(output)
        # await update.message.reply_markdown_v2(output)
    else:
        await update.message.reply_text("Failed.")
    return LLM_MENU

def gemini_send_prompt(prompt_type: str, prompt_input: str):
    print(">> gemini.py > gemini_send_prompt")
    try:
        prompt = prompt_instructions[prompt_type] + prompt_input
        print(f"> prompt = {prompt}")
        client = genai.Client(api_key = gemini_token)
        response = client.models.generate_content(
            model = gemini_model,
            contents = prompt
        )
        return response
    except Exception as e:
        print(f"> Error: {e}")
        return False
    