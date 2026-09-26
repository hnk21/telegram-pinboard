from utility.helper import *

# -------------------------------------------------- #
# Main start node                                    #
# -------------------------------------------------- #

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    name, username = user["first_name"], user["username"]
    print(f"\n>> standard.py > start > User: {username}")
    if username == master:
        message = "\n".join([f"おかえり、{name}\n", get_time(), "/nodes"])
    else:
        message = "\n".join([f"Welcome, {name}", "/nodes"])
    await update.message.reply_text(message)


async def nodes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    username = user["username"]
    if username == master:
        message = "/expense | /bedtime \n/news \n/steam"
        # message = "/expense | /bedtime \n/news | /gemini \n/notion | /steam"
    else:
        message = "/news"
    await update.message.reply_text(message)


async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = "A project by 'https://github.com/hnk21'\n\n"
    message += "Telegram bot as a personal pinboard / assistant"
    await update.message.reply_text(message)


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    name = user["first_name"]
    user_message = update.message.text
    message = f"Hi {name}, I did not understand '{user_message}'"
    await update.message.reply_text(message)


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Returned to main node", reply_markup = ReplyKeyboardRemove())
    return ConversationHandler.END

# -------------------------------------------------- #
# Function for fetching time                         #
# -------------------------------------------------- #

def get_time():
    dt_now = datetime.datetime.now()
    curr_date = dt_now.strftime("%Y-%m-%d | %A")
    dt_end_today = dt_now.replace(hour = 0, minute = 0, second = 0, microsecond = 0) + timedelta(days = 1)
    sec_left = (dt_end_today - dt_now).total_seconds()
    
    hours_left, sec_remain = divmod(sec_left, 3600)
    mins_left, sec = divmod(sec_remain, 60)
    time_left = f"{int(hours_left)} 時間 {int(mins_left)} 分"

    # Convert weekdays from English to Japanese
    weekday = dt_now.strftime("%A")
    youbi = weekdays_en_jp[weekday]
    curr_date = curr_date.replace(weekday, youbi)

    # Get day number of current year
    dt_start = datetime.datetime(dt_now.year, 1, 1)
    days_elapsed = (dt_now - dt_start).days
    days_left = 365 - days_elapsed

    message = f"「 {curr_date} | {days_elapsed + 1} / 365 ({round((days_elapsed + 1) / 365 * 100, 0)}%) 」\n"
    message += f"「 今年の終わり 後 {days_left}日 」\n"
    message += f"「 今日の終わり 後 {time_left} 」\n"
    return message