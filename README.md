# python-telegram-bots
Last updated: 2026-04-25

Personal project, telegram bot as an assistant/pinboard.

Using python-telegram-bot, as the front end interaction

https://docs.python-telegram-bot.org/en/v21.8/index.html

--------------------------------------------------

# To Update Backlog

- **AI node**
    - Google Gemini
    - Prepare different rules to control the response allowed for the LLM, each catered to specific answer requirements
        - General query
        - News article summariser
        - Answer as a certain character (e.g. Chainsawman Pochita)
- **Expense node**
    - Try API to Microsoft OneDrive and update my actual expense Excel
        - https://learn.microsoft.com/en-us/graph/api/resources/onedrive?view=graph-rest-1.0&viewFallbackFrom=odsp-graph-online
    - Analysis, matplotlib
        - Amount spent over each month
- **Sleep node**
    - Data logging from .txt to .db sqlite3
    - Analysis, matplotlib
        - Plot sleep start times
- **Notion node**
    - akr workspace > 2_BUNKA > Japanese vocab training
        - Return overall result of practice (which words ok, which words redo)
    - akr workspace > 1_EVENTS
        - Fetch today's events
        - Fetch this week's events

--------------------------------------------------

# Commands

## Basic

### /start
Starts the bot and display opening message.

### /commands
Displays available commands that starts a node/feature.

### /about
General description about the bot.

--------------------------------------------------

## Public Nodes

### /news
Pulls news article titles and links from selected sites.
- Channel News Asia
    - https://www.channelnewsasia.com/latest-news, for the following categories: 
    - Business, World, Asia, East Asia 
- Ground News
    - https://ground.news/interest/stock-markets
    - https://ground.news/interest/tech
    - https://ground.news/interest/asia
    - https://ground.news/interest/north-america
- NHK Japan
    - https://news.web.nhk/newsweb/genre/, for the following categories:
    - business, society, politics, international

--------------------------------------------------

## Personal Nodes

### /notion
Integration with personal Notion workspace.

### /steam
Fetch my Steam account's info via REST API calls.

### /ai
Google Gemini LLM, feed specific prompt rules for certain actions (Search, Summarise, Check)

### /sleep
For logging sleep timings.

### /expense
For logging simple expenses.

--------------------------------------------------