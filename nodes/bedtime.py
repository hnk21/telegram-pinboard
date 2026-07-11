from utility.helper import *

# States
NODE, ADD, VIEW, ANALYSE, CLEAR = range(5)

# Keyboard reply
reply_keyboard_confirm = [["◯", "☓"]]

# Set log path
log_path = check_file(file = bedtime_log, folder_path = data_path)

# Global variables
next_date = date.today()

# Boilerplate message
return_message = "Returned to bedtime node"

# -------------------------------------------------- #
# Main node                                          #
# -------------------------------------------------- #

async def bedtime_node(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    name, username = user["first_name"], user["username"]
    print(f"\n>> bedtime.py > bedtime_node > User: {username}")
    if username == master:
        message = "\n".join(["- bedtime node -", "/add", "/view", "/analytics"])
    else:
        message = f"Hey '{name}' you can't access this node!"
    await update.message.reply_text(message)
    return NODE

# -------------------------------------------------- #
# Add bedtimes                                       #
# -------------------------------------------------- #

async def add_bedtimes(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    last_date = get_latest_bedtime()
    if last_date:
        message = f"Latest date in log: {last_date}"
    else:
        message = "Bedtime log empty"
    await update.message.reply_text(message)

    global next_date
    next_date = last_date + timedelta(days = 1)
    
    message = "\n".join([f"Enter new bedtimes from {next_date}",
                        "(hhmm ',' separated)"
                        ])
    await update.message.reply_text(message, reply_markup = ReplyKeyboardRemove())
    return ADD

async def add_update_bedtimes(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    input = update.message.text
    await update.message.reply_text(f"Updating bedtime log from {next_date}...")
    success = update_bedtime_log(from_date = next_date, bedtimes = input)
    message = "ok" if success else "failed"
    await update.message.reply_text(message)
    await update.message.reply_text(return_message)
    return NODE

def get_latest_bedtime():
    print(">> bedtime.py > get_latest_bedtime")
    try:
        size = os.path.getsize(log_path)
        if not size:
            print("> Bedtime log empty")
            return False
        else:
            with open(log_path, "r") as log:
                records = log.readlines()
                last_date = records[-1].split(",")[0]
            last_date = date(int(last_date[0:4]), int(last_date[5:7]), int(last_date[8:10]))
            return last_date
    except Exception as e:
        print(f"> Error: {e}")
        print(f"> type = {sys.exc_info()[0]}, line = {sys.exc_info()[2].tb_lineno}")
        return False

def update_bedtime_log(from_date: str, bedtimes: str):
    print(">> bedtime.py > update_bedtime_log")
    try:
        # Split the input string into a list ',' delimiter
        curr_date = from_date
        bedtimes = bedtimes.split(",")
        with open(log_path, "a") as log:
            for time in bedtimes:
                log.write(f"{curr_date},{time}\n")
                curr_date += timedelta(days = 1)
        print(f"> Updated {log_path}")
        return True
    except Exception as e:
        print(f"> Error: {e}")
        print(f"> type = {sys.exc_info()[0]}, line = {sys.exc_info()[2].tb_lineno}")
        return False

# -------------------------------------------------- #
# Get bedtimes                                       #
# -------------------------------------------------- #

async def view_bedtimes(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    dates = get_bedtime_datespan()
    if dates:
        global first_date, last_date
        first_date, last_date = dates[0], dates[1]
        message = f"Enter 'all' to retrieve entire log,\nor a date between {first_date} and {last_date} (yyyymmdd) to start retrieving from"
        await update.message.reply_text(message, reply_markup = ReplyKeyboardRemove())
        return VIEW
    else:
        await update.message.reply_text("Bedtime log empty")
        await update.message.reply_text(return_message)
        return NODE

async def view_get_bedtimes(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    input = update.message.text
    if input == "all":
        from_date = str(first_date)
    else:
        from_date = input
        from_date_ = date(int(from_date[0:4]), int(from_date[4:6]), int(from_date[6:8]))

        if from_date_ < first_date or from_date_ > last_date:
            await update.message.reply_text("Input date does not exists\n" + return_message)
            return NODE
        else:
            from_date = from_date[0:4] + "-" + from_date[4:6] + "-" + from_date[6:8]
    
    await update.message.reply_text(f"Retrieving bedtimes from {from_date}... ")

    result = fetch_bedtimes(from_date = from_date)        
    if result:
        await update.message.reply_text(result[0])
        await update.message.reply_text("\n".join(result[1:]))
    else:
        await update.message.reply_text("failed")
    await update.message.reply_text(return_message)
    return NODE

def get_bedtime_datespan():
    print(f">> bedtime.py > get_bedtime_datespan")
    try:
        size = os.path.getsize(log_path)
        if not size:
            print("> Bedtime log empty")
            return False
        else:
            with open(log_path, "r") as log:
                records = log.readlines()
                first_date = records[0].split(",")[0]
                last_date = records[-1].split(",")[0]
            first_date = date(int(first_date[0:4]), int(first_date[5:7]), int(first_date[8:10]))
            last_date = date(int(last_date[0:4]), int(last_date[5:7]), int(last_date[8:10]))
            return [first_date, last_date]
    except Exception as e:
        print(f"> Error: {e}")
        print(f"> type = {sys.exc_info()[0]}, line = {sys.exc_info()[2].tb_lineno}")
        return False

def fetch_bedtimes(from_date: str):
    print(">> bedtime.py > fetch_bedtimes")
    try:
        with open(log_path, "r") as log:
            result = []
            records = log.readlines()
            log_size = len(records)
            for i in range(log_size - 1, -1, -1):
                entry = records[i]
                date_str, time_str = entry.split(",")
                if i == log_size - 1:
                    end_date = date_str
                result.append(f"{time_str[0:2]}:{time_str[2:4]}")
                if date_str == from_date:
                    break
        if len(result) > 1:
            result.reverse()
            result.insert(0, f"{len(result)} record(s) from {from_date} - {end_date}")
        else:
            result.insert(0, f"Record for {from_date}")
        return result
    except Exception as e:
        print(f"> Error: {e}")
        print(f"> type = {sys.exc_info()[0]}, line = {sys.exc_info()[2].tb_lineno}")
        return False


# -------------------------------------------------- #
# Analytics                                          #
# -------------------------------------------------- #

async def analytics_bedtime(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    size = os.path.getsize(log_path)
    if not size:
        await update.message.reply_text("Bedtime log empty")
        await update.message.reply_text(return_message)
        return NODE
    else:
        with open(log_path, "r") as log:
            records = log.readlines()
        message = f"Enter number of latest days (7 - 31)\n"

        dates = get_bedtime_datespan()
        first_ym, last_ym = str(dates[0])[:7], str(dates[1])[:7]
        if first_ym != last_ym:
            message += f"Or yyyymm from {first_ym} - {last_ym}"
        else:
            message += f"Or {first_ym} in yyyymm"
        
        message += f"\n\nBedtime log has {len(records)} entries"
        await update.message.reply_text(message, reply_markup = ReplyKeyboardRemove())
        return ANALYSE
    
async def analytics_bedtime_plots(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Getting bedtime plot...")

    input = update.message.text
    with open(log_path, "r") as log:
        records = log.readlines()
        # input is a number
        if len(input) <= 2:
            bedtime_data = records[-int(input):]
        # input is yyyymm
        else:
            first, last = None, None
            for i in range(0, len(records)):
                entry = records[i]
                date_str, time_str = entry.split(",")
                if input == date_str[:6] and not first:
                    first = i
                elif input == date_str[:6] and not last:
                    last = i+1
                    break
            bedtime_data = records[first:last]
    
    success = plot_bedtimes(data = bedtime_data)
    if success:
        await update.message.reply_photo(photo = open(data_path + "/" + bedtime_plot_png, 'rb'))
    else:
        await update.message.reply_text("failed")
    
    await update.message.reply_text(return_message)
    return NODE

def plot_bedtimes(data: list) -> bool:
    print(">> bedtime.py > plot_bedtimes")
    try:
        plt.style.use('dark_background')
        fig, ax = plt.subplots(figsize = (19.2, 10.8))

        # Prepare data
        date_data, time_data = list(), list()
        for entry in data:
            date_str, time_str = entry.split(",")
            date_data.append(date_str)
            time_data.append(datetime.time(int(time_str[:2]), int(time_str[2:])))

        x_data = np.array(date_data, dtype = 'datetime64[D]')
        y_data = [datetime.datetime.combine(datetime.date(1997, 7, 30), t) for t in time_data]

        # Plot data
        ax.plot(x_data, y_data, color = "#abb8ac", marker = "x", markersize = 7)
        ax.axhline(y = datetime.datetime(1997, 7, 30, 2, 30, 0), label = "danger", color = "#CC898B", linestyle = "-")
        ax.axhline(y = datetime.datetime(1997, 7, 30, 0, 0, 0), label = "ok", color = "#b8c984", linestyle = "-")

        # Define axis limits
        ax.set_xlim(left = x_data[0], right = x_data[-1])
        ax.set_ylim(bottom = datetime.datetime(1997, 7, 29, 23, 0), top = datetime.datetime(1997, 7, 30, 3, 30))

        # Date and time formatter for axes tickers
        date_formatter = mdates.DateFormatter('%b-%d (%a)')
        ax.xaxis.set_major_formatter(date_formatter)
        time_formatter = mdates.DateFormatter('%H:%M')
        ax.yaxis.set_major_formatter(time_formatter)

        # Title, labels, grid
        ax.set_title(f"Bedtime Plot for {date_data[0]} to {date_data[-1]}")
        ax.set_xlabel("dates")
        ax.set_ylabel("bedtimes")
        ax.grid(True)
        
        # Save plot
        fig.savefig(data_path + "/" + bedtime_plot_png)
        print(f"> Saved plot '{bedtime_plot_png}'")
        return True
    except Exception as e:
        print(f"> Error: {e}")
        print(f"> type = {sys.exc_info()[0]}, line = {sys.exc_info()[2].tb_lineno}")
        return False

# -------------------------------------------------- #
# Clear bedtime data                                 #
# -------------------------------------------------- #

async def clear_bedtime_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    message = "Clear bedtime log - Are you sure?"
    await update.message.reply_text(message, reply_markup = ReplyKeyboardMarkup(reply_keyboard_confirm, resize_keyboard = True, one_time_keyboard = False))
    return CLEAR

async def clear_bedtime_execute(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    confirm = update.message.text
    if confirm == "◯":
        await update.message.reply_text("Clearing bedtime log...")
        success = clear_bedtime()
        message = "ok" if success else "failed"
    else:
        message = "Clear cancelled"
    await update.message.reply_text(message, reply_markup = ReplyKeyboardRemove())
    await update.message.reply_text(return_message)
    return NODE

def clear_bedtime() -> bool:
    print(">> bedtime.py > clear_bedtime")
    try:
        with open(log_path, "w") as log:
            log.truncate(0)
        print(f"> Cleared {log_path}")
        return True
    except Exception as e:
        print(f"> Error: {e}")
        print(f"> type = {sys.exc_info()[0]}, line = {sys.exc_info()[2].tb_lineno}")
        return False