from utility.helper import *
from nodes.standard import *
from nodes.bedtime import *
from nodes.expense import *
from nodes.steam import *
from nodes.news import *

def main(api_token):
    application = Application.builder().token(api_token).concurrent_updates(True).read_timeout(30).write_timeout(30).build()

    ### bedtime handler ###
    bedtime_node_handler = ConversationHandler(
        entry_points = [CommandHandler("bedtime", bedtime_node)],
        states = {NODE: [CommandHandler("add", add_bedtimes),
                         CommandHandler("view", view_bedtimes),
                         CommandHandler("analytics", analytics_bedtime),
                         CommandHandler("clear", clear_bedtime_confirm)
                         ],
                  ADD:  [MessageHandler(filters.Regex("^(?:(?:[0-1][0-9]|2[0-3])[0-5][0-9])(?:,(?:[0-1][0-9]|2[0-3])[0-5][0-9])*$"), add_update_bedtimes)],
                  VIEW: [MessageHandler(filters.Regex("^all|\\d{4}(0[1-9]|1[0-2])(0[1-9]|[12]\\d|3[01])$"), view_get_bedtimes)],
                  ANALYSE: [MessageHandler(filters.Regex("^(?:\\d{4}(?:0[1-9]|1[0-2])|[7-9]|[12]\\d|3[01])$"), analytics_bedtime_plots)],
                  CLEAR : [MessageHandler(filters.Regex("^(◯|✕)$"), clear_bedtime_execute)]
                  },
        fallbacks = [CommandHandler("c", cancel)]
    )
    application.add_handler(bedtime_node_handler)
    
    ### expense handler ###
    expense_node_handler = ConversationHandler(
        entry_points = [CommandHandler("expense", expense_node)],
        states = {NODE: [CommandHandler("add", add_expenses_type),
                         CommandHandler("view", view_expenses),
                         CommandHandler("clear", clear_expense_confirm)
                         ],
                  ADD_TYPE:  [MessageHandler(filters.Regex("^(食|交通|物)$"), add_expenses_amount)],
                  ADD_AMT:  [MessageHandler(filters.Regex("^\\d+(\\.\\d{1,2})?(\\+\\d+(\\.\\d{1,2})?)*$"), add_expenses_update)],
                  GET_DATE: [MessageHandler(filters.Regex("^([0-9]{6}|curr|last)$"), view_expenses_get)],
                  CLEAR : [MessageHandler(filters.Regex("^(◯|✕)$"), clear_expense_execute)]
                  },
        fallbacks = [CommandHandler("c", cancel)]
    )
    application.add_handler(expense_node_handler)

    ### steam handler ###
    steam_node_handler = ConversationHandler(
        entry_points = [CommandHandler("steam", steam_node)],
        states  = {NODE: [CommandHandler("activity", steam_activity),
                          CommandHandler("wishlist", steam_wishlist),
                          CommandHandler("sale", steam_sale)
                          ]
                   },
        fallbacks = [CommandHandler("c", cancel)]
    )
    application.add_handler(steam_node_handler)

    ### news handler ###
    news_node_handler = ConversationHandler(
        entry_points = [CommandHandler("news", news_node)],
        states = {NODE: [CommandHandler("cna", news_cna),
                         CommandHandler("grnd", news_gn),
                         CommandHandler("nhk", news_nhk)
                         ],
                  CNA:  [MessageHandler(filters.Regex("^(Business|World|Singapore|Asia|East Asia)$"), show_cna)],
                  GRND: [MessageHandler(filters.Regex("^(Stock Markets|Tech|Asia|North America)$"), show_gn)],
                  NHK:  [MessageHandler(filters.Regex("^(経済|社会|政治|国際)$"), show_nhk)]
                  },
        fallbacks = [CommandHandler("c", cancel)]
    )
    application.add_handler(news_node_handler)

    ### Handlers for standard and unknown commands ###
    application.add_handlers([CommandHandler("start", start),
                              CommandHandler("nodes", nodes),
                              CommandHandler("about", about),
                              CommandHandler("c", cancel),
                              MessageHandler(filters.TEXT & (~filters.COMMAND), echo)])

    print("\n> main.py > hnk_pinboard bot ONLINE")
    application.run_polling()

# -------------------------------------------------- #
# Run telegram bot                                   #
# -------------------------------------------------- #

try:
    if __name__ == '__main__':
        main(telegram_token)
        print("\n> main.py > hnk_pinboard bot OFFLINE")
except Exception as e:
    print(f"\n> main.py > Failed to start hnk_pinboard bot > Error: {e}")
    print(f"> type = {sys.exc_info()[0]}, line = {sys.exc_info()[2].tb_lineno}")