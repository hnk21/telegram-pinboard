from utility.helper import *
from utility.formatter import format_markdown

# States
STEAMMENU = range(1)

# -------------------------------------------------- #
# Main node                                          #
# -------------------------------------------------- #

async def steam_node(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    name, username = user["first_name"], user["username"]
    print(f"\n>> steam.py > steam_node > User: {username}")
    if username == master:
        message = "\n".join(["- steam node -",
                            "/activity - Recent playtime",
                            "/wishlist - Wishlist",
                            "/sale - Next seasonal sale"
                            ])
    else:
        message = f"Hey '{name}' you can't access this node!"
    await update.message.reply_text(message)
    return STEAMMENU

# -------------------------------------------------- #
# State functions                                    #
# -------------------------------------------------- #

async def steam_activity(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(">> steam.py > steam_activity")
    message = "Fetching recent play activity..."
    await update.message.reply_text(message)
    
    success = get_recently_played()

    if success:
        with open(json_folder_path + "/" + steam_json_1, "r") as json_file:
            data = json.load(json_file)
        data = data["response"]
        number_played = data["total_count"]
        message = f"Played {number_played} games for the past 2 weeks:\n\n"
        
        recent_playtime_min = 0
        games_played = data["games"]
        
        for game in games_played:
            recent_playtime_min += game["playtime_2weeks"]
            message += f"・ '{game["name"]}', {round(game["playtime_2weeks"] / 60, 1)} hours\n"
        recent_playtime_hour = round(recent_playtime_min / 60, 1)
        message += f"\nTotal hours: {recent_playtime_hour}"
    else:
        message = "Failed, returned to steam node"
    await update.message.reply_text(message)
    return STEAMMENU

async def steam_wishlist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(">> steam.py > steam_wishlist")
    message = "Fetching your wishlist info..."
    await update.message.reply_text(message)
    # Check if .json file needs updating
    hours = 24
    to_update, json_path = check_file_update(file = steam_json_2, folder_path = json_folder_path, hours = 24)
    if to_update:
        print("> Running get_wishlist to get .json file...")
        success = get_wishlist()
    else:
        print(f"> '{json_path}' was last modified < {hours} hours ago, skipping fetching step")
        success = True
    if success:
        with open(json_folder_path + "/" + steam_json_2, "r") as json_file:
            data = json.load(json_file)
        i = 1
        result = []
        for game in data.keys():
            name, price, discount = data[game]["name"], data[game]["price"], data[game]["discount"]
            if name != '-' and price != '-':
                price = price.replace("S", "")
                result.append([name, price, discount])
        
        # Sort in order of discounted games, ascending price of games, games not released yet
        result_sorted = sorted(result, key = lambda d: (-d[2], d[1]))
        message = [f"__Fetched {len(data)} games from your wishlist__"]
        total_cost = 0 
        for i in range(len(result_sorted)):
            g = result_sorted[i]
            name, price, discount = g[0], g[1], g[2]
            if discount > 0:
                message.append(f"> {i+1}\\. {format_markdown(name)}, {format_markdown(price)}, *{discount}% off*")
                total_cost += float(g[1][1:])
            elif discount == "-":
                message.append(f"{i+1}\\. {format_markdown(name)}, not released")
            else:
                message.append(f"{i+1}\\. {format_markdown(name)}, {format_markdown(price)}")
                total_cost += float(g[1][1:])
        message = "\n".join(message)
        message += f"\n\nTotal: ${format_markdown(str(round(total_cost, 2)))}"
        await update.message.reply_markdown_v2(message)
    else:
        message = "Failed, returned to steam node"
        await update.message.reply_text(message)
    return STEAMMENU

async def steam_sale(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = "https://steamdb.info/sales/history/"
    message = f"Visit '{url}' for news on the next seasonal Steam sale"
    await update.message.reply_text(message)
    return STEAMMENU

# -------------------------------------------------- #
# API functions                                      #
# -------------------------------------------------- #

def get_recently_played():
    print(">> steam.py > get_recently_played")
    print("> GET - recently played games", end = " ")
    url = f"https://api.steampowered.com/IPlayerService/GetRecentlyPlayedGames/v0001/?key={steam_token}&steamid={steam_id}&format=json"
    response = requests.get(url)
    status = response.status_code
    if status == 200:
        print(f"> {status} ok")
        data = response.json()
        with open(json_folder_path + "/" + steam_json_1, 'w') as file:
            json.dump(data, file, indent=4)
        return True
    else:
        print(f"> {status} failed")
        return False

# 3 GET requests
    # 1. Get wishlist from steam user
    # 2. Get current price of all games in wishlist
    # 3. Get game name

def get_wishlist():
    print(">> steam.py > get_wishlist")
    try:
        # 1. Get wishlist
        print(f"> GET steam user wishlist", end = " ")
        wishlist_url = f"https://api.steampowered.com/IWishlistService/GetWishlist/v1/?key={steam_token}&steamid={steam_id}&format=json"
        response = requests.get(wishlist_url)
        status = response.status_code
        if status == 200:
            print(f"> {status} ok")
            wishlist_data = response.json()["response"]["items"]
            print(f"> Retrieved {len(wishlist_data)} games from wishlist")
            if len(wishlist_data) > 0:
                result = defaultdict()
                appids = []
                for game in wishlist_data:
                    appids.append(str(game["appid"]))
                # 2. Get current price of all games in wishlist
                print(f"> GET steam game prices", end = " ")
                string_appids = ",".join(appids)
                game_prices_url = f"http://store.steampowered.com/api/appdetails?appids={string_appids}&filters=price_overview"
                response = requests.get(game_prices_url)
                status = response.status_code

                if status == 200:
                    print(f"> {status} ok")
                    game_price_data = response.json()
                    for appid in appids:
                        # 3. Get game name
                        print(f"> GET steam details > {appid}", end = " ")
                        game_url = f"http://store.steampowered.com/api/appdetails?appids={appid}"
                        response = requests.get(game_url)
                        status = response.status_code
                        if status == 200:
                            print(f"> {status} ok")
                            game_name = response.json()[appid]["data"]["name"]
                            game_data = game_price_data[appid]["data"]
                            if game_data:
                                price_data = game_data["price_overview"]
                                currency, discount_percent, price = price_data["currency"], price_data["discount_percent"], price_data["final_formatted"]
                                result[appid] = {"name": game_name, "price": price, "discount": discount_percent, "currency": currency}
                            else:
                                result[appid] = {"name": game_name, "price": '-', "discount": '-', "currency": '-'}
                        else:
                            result[appid] = {"name": '-', "price": '-', "discount": '-', "currency": '-'}
                            print(f"> {status} failed")
                    with open(json_folder_path + "/" + steam_json_2, 'w') as file:
                        json.dump(result, file, indent = 4)
                        print(f"> Wrote wishlist data to {steam_json_2}")
                    return True
                else:
                    print(f"> {status} failed")
                    return False
            else:
                print("> Wishlist is empty")
                return False
        else:
            print(f"> {status} failed")
            return False
    except Exception as error:
        print(f"> Error > {error}")
        return False