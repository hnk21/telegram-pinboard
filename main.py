from utility.helper import *
from nodes.standard import *
from nodes.sleep import *
from nodes.news import *
from nodes.expense import *
from nodes.notion import *
from nodes.steam import *
from nodes.gemini import *

def main(api_token):
    application = Application.builder().token(api_token).concurrent_updates(True).read_timeout(30).write_timeout(30).build()

    ### news handler ###
    news_node_handler = ConversationHandler(
        entry_points = [CommandHandler("news", news_node)],
        states = {NEWSMENU: [CommandHandler("cna", news_cna),
                             CommandHandler("grnd", news_gn),
                             CommandHandler("nhk", news_nhk)
                             ],
                  CNA:  [MessageHandler(filters.Regex("^(Asia|Business|East Asia|World)$"), show_cna)],
                  GRND: [MessageHandler(filters.Regex("^(Stock Markets|Tech|Asia|North America)$"), show_gn)],
                  NHK:  [MessageHandler(filters.Regex("^(経済|社会|政治|国際)$"), show_nhk)]
                  },
        fallbacks = [CommandHandler("c", cancel)]
    )
    application.add_handler(news_node_handler)

    ### gemini handler (Google Gemini) ###
    gemini_node_handler = ConversationHandler(
        entry_points = [CommandHandler("gemini", gemini_node)],
        states  = {LLM_MENU: [MessageHandler(filters.Regex("^(search|check|summarise|free)$"), gemini_input_prompt)]
                   },
        fallbacks = [CommandHandler("c", cancel)]
    )
    application.add_handler(gemini_node_handler)
    
    ### sleep handler ###
    sleep_node_handler = ConversationHandler(
        entry_points = [CommandHandler("sleep", sleep_node)],
        states = {SLEEPMENU: [CommandHandler("add", sleep_add),
                              CommandHandler("view", sleep_view),
                              CommandHandler("clear", sleep_clear_confirm)
                              ],
                  SLEEPADD:  [MessageHandler(filters.Regex("^(?:(?:[0-1][0-9]|2[0-3])[0-5][0-9])(?:,(?:[0-1][0-9]|2[0-3])[0-5][0-9])*$"), sleep_add_update)],
                  SLEEPVIEW: [MessageHandler(filters.Regex("^\\d{4}(0[1-9]|1[0-2])(0[1-9]|[12]\\d|3[01])$"), sleep_view_get)],
                  SLEEPCLEAR : [MessageHandler(filters.Regex("^(◯|✕)$"), sleep_clear_execute)]
                  },
        fallbacks = [CommandHandler("c", cancel)]
    )
    application.add_handler(sleep_node_handler)

    ### expense handler ###
    expense_node_handler = ConversationHandler(
        entry_points = [CommandHandler("expense", expense_node)],
        states = {EXPMENU: [CommandHandler("add", expense_add_type),
                            CommandHandler("view", expense_view_date),
                            CommandHandler("clear", expense_clear_confirm)
                            ],
                  EXPADD_TYPE:  [MessageHandler(filters.Regex("^(食|交通|物)$"), expense_add_amount)],
                  EXPADD_AMT:  [MessageHandler(filters.Regex("^\\d+(\\.\\d{1,2})?(\\+\\d+(\\.\\d{1,2})?)*$"), expense_add_update)],
                  EXPGET_DATE: [MessageHandler(filters.Regex("^([0-9]{6}|curr|last)$"), expense_view_get)],
                  EXPCLEAR : [MessageHandler(filters.Regex("^(◯|✕)$"), expense_clear_execute)]
                  },
        fallbacks = [CommandHandler("c", cancel)]
    )
    application.add_handler(expense_node_handler)

    ### munni handler (Excel) ###
    # munni_node_handler = ConversationHandler(
    #     entry_points = [CommandHandler("munni", munni_node)],
    #     states = {MENU: [CommandHandler("add", munni_function),
    #                         CommandHandler("view", munni_function)
    #                         ],
    #               STATE_:  [MessageHandler(filters.Regex("^(食|交通|物)$"), expense_add_amount)],
    #               },
    #     fallbacks = [CommandHandler("c", cancel)]
    # )
    # application.add_handler(munni_node_handler)

    ### notion handler ###
    notion_node_handler = ConversationHandler(
        entry_points = [CommandHandler("notion", notion_node)],
        states  = {NOTIONMENU: [CommandHandler("jpvocab", notion_jpvocab)
                                # CommandHandler("telegram_command", notion_function),
                                # CommandHandler("telegram_command", notion_function)
                                ],
                   JP_VOCAB_GET: [MessageHandler(filters.Regex("^([1-9]|[12][0-9]|30)$"), notion_jpvocab_get)],
                   JP_VOCAB_ANS: [MessageHandler(filters.Regex("^(Start|◯|☓)$"), notion_jpvocab_ans)],
                   JP_VOCAB_UPD: [MessageHandler(filters.Regex("^(◯|☓)$"), notion_jpvocab_update)]
                   },
        fallbacks = [CommandHandler("c", cancel)]
    )
    application.add_handler(notion_node_handler)

    ### steam handler ###
    steam_node_handler = ConversationHandler(
        entry_points = [CommandHandler("steam", steam_node)],
        states  = {STEAMMENU: [CommandHandler("activity", steam_activity),
                               CommandHandler("wishlist", steam_wishlist),
                               CommandHandler("sale", steam_sale)
                               ]
                   },
        fallbacks = [CommandHandler("c", cancel)]
    )
    application.add_handler(steam_node_handler)

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