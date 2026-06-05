# python-telegram-bots
Last updated: 2026-06

Personal project, telegram bot as an assistant/pinboard.

Using python-telegram-bot, as the front end interaction

https://docs.python-telegram-bot.org/en/v21.8/index.html

--------------------------------------------------

# Commands

## Basic

### /start
Starts the bot and display opening message.

### /nodes
Displays available nodes.

### /about
General description about this project.

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

### /gemini
Google Gemini Large Language Model

Feed defined rules for following types of things the LLM is to do:

- Search
    - ...
- Check
    - ...
- Summarise
    - Provide a link to a source article, then return a summary of that article
    - Notes/Findings: Large langauge models are just text predictors
    - As expected, it cannot/are not capable of doing this, they literally make stuff up from the provided article link given, and the contents of the "original article" it returns changes for each fresh prompt provided for the same link
    - It cannot do the action of accessing the link and fetching and parsing the contents of the article, need to scrape the contents of the article and then feed it

--------------------------------------------------

## Personal Nodes

### /notion
Integration with personal Notion workspace.

### /steam
Fetch my Steam account's info via REST API calls.

### /sleep
For logging sleep timings.

### /expense
For logging simple expenses.

--------------------------------------------------