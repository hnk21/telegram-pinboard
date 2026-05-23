from utility.helper import *

# States
EXPMENU, EXPADD_TYPE, EXPADD_AMT, EXPGET_TYPE, EXPGET_DATE, EXPCLEAR = range(6)

# Keyboard reply
reply_keyboard_type = [["食", "交通", "物"]]
reply_keyboard_confirm = [["◯", "✕"]]

# Expense log
expenselog_path = check_file(file = expense_log, folder_path = data_path)

# Global variables
exp_type = str()

# -------------------------------------------------- #
# Main node menu                                     #
# -------------------------------------------------- #

async def expense_node(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    name, username = user["first_name"], user["username"]
    print(f"\n>> expense.py > expense_node > User: {username}")
    if username == master:
        message = "\n".join(["- expense node -",
                            "/add - Add an expense",
                            "/view - View expenses",
                            "/cancel - Exit node"
                            ])
    else:
        message = f"Hey '{name}' you can't access this node!"
    await update.message.reply_text(message)
    return EXPMENU

# -------------------------------------------------- #
# Functions for adding expense                       #
# -------------------------------------------------- #

async def expense_add_type(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    message = "Add expenses - Select type"
    await update.message.reply_text(message, reply_markup = ReplyKeyboardMarkup(reply_keyboard_type, resize_keyboard = True, one_time_keyboard = False))
    return EXPADD_TYPE

async def expense_add_amount(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    global input_type
    input_type = update.message.text
    message = "Enter amount(s), '+' separated"
    await update.message.reply_text(message, reply_markup = ReplyKeyboardRemove())
    return EXPADD_AMT

async def expense_add_update(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    message = "Updating expense log..."
    await update.message.reply_text(message)
    input_amounts = update.message.text
    exp_date = date.today().strftime("%Y-%m-%d")
    success = expense_update(expense_date = exp_date, expense_type = input_type, expense_amounts = input_amounts)
    message = "ok" if success else "failed"
    await update.message.reply_text(message)
    return EXPMENU

def expense_update(expense_date: str, expense_type: str, expense_amounts: str):
    print(f">> expense_node.py > expense_update")
    try:        
        if "+" in expense_amounts:
            expenses = expense_amounts.split("+")
            total_amount = 0
            for i in expenses:
                total_amount += float(i)
        else:
            total_amount = float(expense_amounts)
        total_amount = str(round(total_amount, 2))
        with open(expenselog_path, "a") as log:
            log.write(f"{expense_date},{expense_type},{total_amount}\n")
            print(f"> Added expense: {expense_date},{expense_type},{total_amount}")
        return True
    except Exception as e:
        print(f"> Error: {e}")
        return False

# -------------------------------------------------- #
# Functions for fetching from expense log            #
# -------------------------------------------------- #

async def expense_view_type(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    got_data = expense_check_log()
    if got_data:
        message = "View expenses - Select type"
        await update.message.reply_text(message, reply_markup = ReplyKeyboardMarkup(reply_keyboard_type, resize_keyboard = True, one_time_keyboard = False, input_field_placeholder = "Select type of expense"))
        return EXPGET_TYPE
    else:
        message = "Expense log is empty"
        await update.message.reply_text(message)
        return EXPMENU

async def expense_view_date(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    global input_type
    input_type = update.message.text
    message = "Enter year-month (yyyymm)"
    await update.message.reply_text(message, reply_markup = ReplyKeyboardRemove())
    return EXPGET_DATE

async def expense_view_get(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    input_yearmonth = update.message.text
    message = f"Retrieving total '{input_type}' expense for {input_yearmonth}...\n"
    await update.message.reply_text(message)
    result = expense_get(expense_type = input_type, yearmonth = input_yearmonth)
    message = result if result else "failed"
    await update.message.reply_text(message)
    return EXPMENU

def expense_check_log():
    try:
        if os.path.getsize(expenselog_path) == 0:
            print("> Expense log empty")
            return False
        else:
            return True
    except Exception as e:
        print(f"> Error: {e}")
        return False

def expense_get(expense_type: str, yearmonth: str):
    print(">> expense_node.py > expense_get")
    try:
        expense_sum = float()
        with open(expenselog_path, "r") as log:
            expenses = log.readlines()
            for exp in expenses:
                e = exp.split(",")
                e_date, e_type, e_amount = e[0], e[1], e[2]
                e_yearmonth = e_date[0:4] + e_date[5:7]
                if e_yearmonth == yearmonth and e_type == expense_type:
                    expense_sum += float(e_amount)
        get_result = f"Total Amount = ${round(expense_sum, 2)}"
        print(f"> Retrieved {expense_type} expenses for {yearmonth}")
        return get_result
    except Exception as e:
        print(f"> Error: {e}")
        return False

# -------------------------------------------------- #
# Functions for clearing expense data                #
# -------------------------------------------------- #

async def expense_clear_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    message = "Clear expense log - Are you sure?"
    await update.message.reply_text(message, reply_markup = ReplyKeyboardMarkup(reply_keyboard_confirm, resize_keyboard = True, one_time_keyboard = False))
    return EXPCLEAR

async def expense_clear_execute(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    confirm = update.message.text
    if confirm == "◯":
        message = "Clearing expense log..."
        await update.message.reply_text(message)
        success = expense_clear()
        message = "ok" if success else "failed"
    else:
        message = "Clear cancelled"
    await update.message.reply_text(message, reply_markup = ReplyKeyboardRemove())
    return EXPMENU

def expense_clear():
    print(">> expense_node.py > expense_clear")
    try:
        with open(expenselog_path, "w") as log:
            log.truncate(0)
        print(f"> Cleared {expenselog_path}")
        return True
    except Exception as e:
        print(f"> Error: {e}")
        return False