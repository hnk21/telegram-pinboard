from utility.helper import *

# States
SLEEPMENU, SLEEPADD, SLEEPVIEW, SLEEPCLEAR = range(4)

# Keyboard reply
reply_keyboard_confirm = [["◯", "✕"]]

# Sleep log
sleeplog_path = check_file(file = sleep_log, folder_path = data_path)

# Global variables
next_date = date.today()

# -------------------------------------------------- #
# Main node                                          #
# -------------------------------------------------- #

async def sleep_node(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    name, username = user["first_name"], user["username"]
    print(f"\n>> sleep_node.py > sleep_node > User: {username}")
    if username == master:
        message = "\n".join(["| sleep node",
                            "/add - Add sleep timings",
                            "/view - View sleep log"
                            ])
    else:
        message = f"Hey '{name}' you can't access this node!"
    await update.message.reply_text(message)
    return SLEEPMENU

# -------------------------------------------------- #
# Add sleep records                                  #
# -------------------------------------------------- #

async def sleep_add(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    global next_date
    last_date = sleep_get_last_date()

    # Sleep log not empty
    if last_date:
        message = f"Latest date in sleep log: {last_date}"
        next_date = last_date + timedelta(days = 1)
    # Sleep log empty
    else:
        message = "Sleep log is empty"
    
    await update.message.reply_text(message)
    
    message = "\n".join([f"Enter new sleep timings from {next_date}",
                       "(hhmm ',' separated)"
                       ])
    await update.message.reply_text(message, reply_markup = ReplyKeyboardRemove())
    return SLEEPADD

async def sleep_add_update(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    sleep_times = update.message.text
    message = f"Updating sleep log from {next_date}..."
    await update.message.reply_text(message)
    success = sleep_update(from_date = next_date, new_times = sleep_times)
    message = "ok" if success else "failed"
    await update.message.reply_text(message)
    return SLEEPMENU

def sleep_get_last_date():
    print(f">> sleep_node.py > sleep_get_last_date")
    try:
        if os.path.getsize(sleeplog_path) == 0:
            print("> Sleep log is empty")
            return False
        else:
            with open(sleeplog_path, "r") as log:
                records = log.readlines()
                last_date = records[-1].split(",")[0]
            last_date = date(int(last_date[0:4]), int(last_date[5:7]), int(last_date[8:10]))
            return last_date
    except Exception as e:
        print(f"> Error: {e}")
        return False

def sleep_update(from_date: str, new_times: str):
    print(f">> sleep_node.py > sleep_update")
    try:
        # Split the input string into a list ',' delimiter
        curr_date = from_date
        new_times = new_times.split(",")
        with open(sleeplog_path, "a") as log:
            for time in new_times:
                log.write(f"{curr_date},{time}\n")
                curr_date += timedelta(days = 1)
        print(f"> Updated {sleeplog_path}")
        return True
    except Exception as e:
        print(f"> Error: {e}")
        return False

# -------------------------------------------------- #
# Get sleep data                                     #
# -------------------------------------------------- #

async def sleep_view(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    dates = sleep_get_dates()
    if dates:
        global first_date, last_date
        first_date, last_date = dates[0], dates[1]
        message = f"Enter a date 'yyyymmdd' between {first_date} and {last_date} to retrieve the sleep timings from"
        await update.message.reply_text(message, reply_markup = ReplyKeyboardRemove())
        return SLEEPVIEW
    else:
        message = "Sleep log is empty"
        await update.message.reply_text(message)
        return SLEEPMENU

async def sleep_view_get(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    from_date = update.message.text
    dt_from = date(int(from_date[0:4]), int(from_date[4:6]), int(from_date[6:8]))
    if dt_from < first_date or dt_from > last_date:
        message = "Input date does not exist in sleep log"
        await update.message.reply_text(message)
    else:
        from_date = from_date[0:4] + "-" + from_date[4:6] + "-" + from_date[6:8]
        message = f"Retrieving sleep logs from {from_date}..."
        await update.message.reply_text(message)
        result = sleep_fetch(from_date = from_date)        
        if result:
            await update.message.reply_text(result)
        else:
            await update.message.reply_text("failed")
    return SLEEPMENU

def sleep_get_dates():
    print(f">> sleep_node.py > sleep_get_dates")
    try:
        if os.path.getsize(sleeplog_path) == 0:
            print("> Sleep log empty")
            return False
        else:
            with open(sleeplog_path, "r") as log:
                records = log.readlines()
                first_date = records[0].split(",")[0]
                last_date = records[-1].split(",")[0]
            first_date = date(int(first_date[0:4]), int(first_date[5:7]), int(first_date[8:10]))
            last_date = date(int(last_date[0:4]), int(last_date[5:7]), int(last_date[8:10]))
            return [first_date, last_date]
    except Exception as e:
        print(f"> Error: {e}")
        return False

def sleep_fetch(from_date: str):
    print(f">> sleep_node.py > sleep_fetch")
    try:
        with open(sleeplog_path, "r") as log:
            result = []
            records = log.readlines()
            log_size = len(records)

            for i in range(log_size - 1, -1, -1):
                sleep_entry = records[i]
                date_str, time_str = sleep_entry.split(",")
                if i == log_size - 1:
                    end_date = date_str
                result.append(f"{time_str[0:2]}:{time_str[2:4]}")
                if date_str == from_date:
                    break
        if len(result) > 1:
            result.reverse()
            result.insert(0, f"{len(result)} record(s) from {from_date} > {end_date}")
        else:
            result.insert(0, f"Record for {from_date}")
        return "\n".join(result)
    except Exception as e:
        print(f"> Error: {e}")
        return False

# -------------------------------------------------- #
# Sleep analytics                                    #
# -------------------------------------------------- #

# async def sleep_analytics_(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # return

# select duration: past x days
# do analytics, return result plot



# -------------------------------------------------- #
# Clear sleep data                                   #
# -------------------------------------------------- #

async def sleep_clear_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    message = "Clear all sleep data - Are you sure?"
    await update.message.reply_text(message, reply_markup = ReplyKeyboardMarkup(reply_keyboard_confirm, resize_keyboard = True, one_time_keyboard = False))
    return SLEEPCLEAR

async def sleep_clear_execute(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    confirm = update.message.text
    if confirm == "◯":
        message = "Clearing sleep data..."
        await update.message.reply_text(message)
        success = sleep_clear()
        message = "ok" if success else "failed"
    else:
        message = "Clear cancelled, returned to sleep node"
    await update.message.reply_text(message, reply_markup = ReplyKeyboardRemove())
    return SLEEPMENU

def sleep_clear():
    print(">> sleep_node.py > sleep_clear")
    try:
        with open(sleeplog_path, "w") as log:
            log.truncate(0)
        print(f"> Cleared {sleeplog_path}")
        return True
    except Exception as e:
        print(f"> Error: {e}")
        return False