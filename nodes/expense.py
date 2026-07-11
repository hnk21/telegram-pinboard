from utility.helper import *

# States
NODE, ADD_TYPE, ADD_AMT, GET_DATE, CLEAR = range(5)

# Keyboard reply
reply_keyboard_type = [["食", "交通", "物"]]
reply_keyboard_confirm = [["◯", "☓"]]

# Set log path
log_path = check_file(file = expense_log, folder_path = data_path)

# Boilerplate message
return_message = "Returned to expense node"

# -------------------------------------------------- #
# Main node                                          #
# -------------------------------------------------- #

async def expense_node(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    name, username = user["first_name"], user["username"]
    print(f"\n>> expense.py > expense_node > User: {username}")
    if username == master:
        message = "\n".join(["- expense node -", "/add", "/view"])
    else:
        message = f"Hey '{name}' you can't access this node!"
    await update.message.reply_text(message)
    return NODE

# -------------------------------------------------- #
# Add expenses                                       #
# -------------------------------------------------- #

async def add_expenses_type(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    message = "Add expenses - Select type"
    await update.message.reply_text(message, reply_markup = ReplyKeyboardMarkup(reply_keyboard_type, resize_keyboard = True, one_time_keyboard = False))
    return ADD_TYPE

async def add_expenses_amount(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    global input_type
    input_type = update.message.text
    message = "Enter amount(s), '+' separated"
    await update.message.reply_text(message, reply_markup = ReplyKeyboardRemove())
    return ADD_AMT

async def add_expenses_update(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    input_amounts = update.message.text
    exp_date = date.today().strftime("%Y-%m-%d")
    await update.message.reply_text("Updating expense log...")
    success = update_expense_log(expense_date = exp_date, expense_type = input_type, expense_amounts = input_amounts)
    message = "ok" if success else "failed"
    await update.message.reply_text(message)
    await update.message.reply_text(return_message)
    return NODE

def update_expense_log(expense_date: str, expense_type: str, expense_amounts: str) -> bool:
    print(">> expense.py > update_expense_log")
    try:        
        if "+" in expense_amounts:
            expenses = expense_amounts.split("+")
            total_amount = 0
            for i in expenses:
                total_amount += float(i)
        else:
            total_amount = float(expense_amounts)
        total_amount = str(round(total_amount, 2))
        with open(log_path, "a") as log:
            log.write(f"{expense_date},{expense_type},{total_amount}\n")
            print(f"> Added expense: {expense_date},{expense_type},{total_amount}")
        return True
    except Exception as e:
        print(f"> Error: {e}")
        print(f"> type = {sys.exc_info()[0]}, line = {sys.exc_info()[2].tb_lineno}")
        return False

# -------------------------------------------------- #
# Get expense data for specific year month           #
# -------------------------------------------------- #

async def view_expenses(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    got_data = check_expense_log()
    if got_data:
        message = "curr - Current month\nlast - Last month\nOr enter yyyymm"
        await update.message.reply_text(message)
        return GET_DATE
    else:
        await update.message.reply_text("Expense log empty")
        await update.message.reply_text(return_message)
        return NODE

async def view_expenses_get(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    input = update.message.text
    print(f"view_get > input = {input}")

    if input == "curr":
        yearmonth = datetime.datetime.today().strftime("%Y%m")
    elif input == "last":
        last_month = datetime.datetime.today().replace(day = 1) - timedelta(days = 1)
        yearmonth = last_month.strftime("%Y%m")
    else:
        yearmonth = input
    await update.message.reply_text(f"Retrieving expenses for {yearmonth}...")

    result = get_expenses(yearmonth = yearmonth)
    if result:
        total_amount = float()
        for exp_type in result.keys():
            message = f"> {exp_type} = ${round(result[exp_type], 2)}\n"
            total_amount += result[exp_type]
        message += f">> Total = ${round(total_amount, 2)}"
        await update.message.reply_text(message)
    else:
        await update.message.reply_text("failed")
    await update.message.reply_text(return_message)
    return NODE

def check_expense_log() -> bool:
    print(">> expense.py > check_expense_log")
    try:
        size = os.path.getsize(log_path)
        if not size:
            print("> Expense log empty")
            return False
        else:
            return True
    except Exception as e:
        print(f"> Error: {e}")
        return False

def get_expenses(yearmonth: str):
    print(">> expense.py > get_expenses")
    try:
        result = defaultdict(float)
        with open(log_path, "r") as log:
            expenses = log.readlines()
            for exp in expenses:
                e = exp.split(",")
                e_date, e_type, e_amount = e[0], e[1], e[2]
                e_yearmonth = e_date[0:4] + e_date[5:7]
                if e_yearmonth == yearmonth:
                    result[e_type] += float(e_amount)
        print(f"> Retrieved expenses for {yearmonth}")
        return result
    except Exception as e:
        print(f"> Error: {e}")
        print(f"> type = {sys.exc_info()[0]}, line = {sys.exc_info()[2].tb_lineno}")
        return False

# -------------------------------------------------- #
# Expense analytics                                  #
# -------------------------------------------------- #

# async def expense_analytics_(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # return

# select expense type
# select period: this year, this month
# do analytics, return result plot


# -------------------------------------------------- #
# Clear expense data                                 #
# -------------------------------------------------- #

async def clear_expense_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    message = "Clear expense log - Are you sure?"
    await update.message.reply_text(message, reply_markup = ReplyKeyboardMarkup(reply_keyboard_confirm, resize_keyboard = True, one_time_keyboard = False))
    return CLEAR

async def clear_expense_execute(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    confirm = update.message.text
    if confirm == "◯":
        message = "Clearing expense log..."
        await update.message.reply_text(message)
        success = clear_expense()
        message = "ok" if success else "failed"
    else:
        message = "Clear cancelled"
    await update.message.reply_text(message, reply_markup = ReplyKeyboardRemove())
    await update.message.reply_text(return_message)
    return NODE

def clear_expense() -> bool:
    print(">> expense.py > clear_expense")
    try:
        with open(log_path, "w") as log:
            log.truncate(0)
        print(f"> Cleared {log_path}")
        return True
    except Exception as e:
        print(f"> Error: {e}")
        print(f"> type = {sys.exc_info()[0]}, line = {sys.exc_info()[2].tb_lineno}")
        return False