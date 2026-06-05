from utility.helper import *

# -------------------------------------------------- #
# Main scraper                                       #
# -------------------------------------------------- #

async def scrape_html(url: str, html_path: str) -> bool:
    print(f">> scraper.py > scrape_html > Connecting to '{url}'...")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.ok:
                    print(f"> ({response.status}) connection success")
                    html = await response.text()
                    with open(html_path, "w", encoding="utf-8") as f:
                        f.write(html)
                    print(f"> Updated '{html_path}'")
                    return True
                else:
                    print(f"({response.status}) connection error")
                    return False
    except Exception as e:
        print(f"> Error: {e}")
        return False

# -------------------------------------------------- #
# Channel News Asia html scraper                     #
# -------------------------------------------------- #

async def parse_html_cna():
    print(f">> scraper.py > parse_html_cna")
    
    file_path = check_file(file = cna_html, folder_path = html_folder_path)
    success = asyncio.get_event_loop().create_task(scrape_html(url = cna_url, html_path = file_path))
    await success

    if success:    
        with open(file_path, 'r', encoding = 'utf-8') as file:
            html_content = file.read()
        
        soup = BeautifulSoup(html_content, 'html.parser')

        # Grab tags with attribute 'data-category' that are in defined categories
        # Then get attributes 'data-category', 'data-heading', 'data-link_absolute'
        categories = ["Business", "World", "Asia", "East Asia"]
        tags = soup(attrs = {"data-category": categories})
        news_dict = defaultdict(list)
        for tag in tags:
            category = tag["data-category"]
            link     = tag["data-link_absolute"]
            title    = tag["data-heading"]
            news_dict[category].append([title, link])
        
        # Save news_dict into .json
        with open(json_folder_path + "/" + cna_json, 'w') as file:
            json.dump(news_dict, file, indent = 4)
        
        print(f"> Updated {cna_json} in {data_path}")
    else:
        print(f"> Could not scrape from '{cna_url}'")

# -------------------------------------------------- #
# Ground News html scraper                           #
# -------------------------------------------------- #

async def parse_html_gn():
    print(f">> scraper.py > parse_html_gn")

    news_dict = defaultdict(list)

    for topic in gn_topics:
        gn_url_topic = gn_url + topic
        gn_html = "news_gn_" + topic + ".html"
        file_path = check_file(file = gn_html, folder_path = html_folder_path)

        success = asyncio.get_event_loop().create_task(scrape_html(url = gn_url_topic, html_path = file_path))
        await success

        if success:
            with open(file_path, 'r', encoding='utf-8') as file:
                html_content = file.read()
            soup = BeautifulSoup(html_content, 'html.parser')

            ## (1) Grab attributes 'href', which are article links when appended to https://ground.news/ 
            ## (2) Make the article title from these links
            ## Remove /article/
            ## Replace "-" characters with " "
            ## Ignore string past "_" if any
            ## Capitalise first character of each word
            
            tags = soup(filter_attr_href)
            articles = set()

            for tag in tags:
                if "article" in tag["href"] and tag["href"] not in articles:
                    link = tag["href"]
                    articles.add(link)
                    title = " ".join( [word.capitalize() for word in link[9:].split("-")] )
                    news_dict[gn_topics[topic]].append([title, gn_base + link])
        else:
            print(f"> Could not scrape from '{gn_url_topic}' ...")
        
    # Save news_dict into .json
    with open(json_folder_path + "/" + gn_json, 'w') as file:
        json.dump(news_dict, file, indent = 4)
    
    print(f"> Updated {gn_json} in {data_path}")

# -------------------------------------------------- #
# NHK Japan html scraper                             #
# -------------------------------------------------- #

async def parse_html_nhk():
    print(f">> scraper.py > parse_html_nhk")

    news_dict = defaultdict(list)

    for topic_en, topic_jp in nhk_topics.items():
        nhk_url_topic = nhk_url + topic_en
        nhk_html = "news_nhk_" + topic_en + ".html"

        file_path = check_file(file = nhk_html, folder_path = html_folder_path)
        success = asyncio.get_event_loop().create_task(scrape_html(url = nhk_url_topic, html_path = file_path))
        await success

        if success:    
            with open(file_path, 'r', encoding='utf-8') as file:
                html_content = file.read()
            
            soup = BeautifulSoup(html_content, 'html.parser')

            articles = soup.select('a[href^="https://news.web.nhk/newsweb/na"]')
            for article in articles:
                link = article['href']
                # title_tag = article.select_one('strong')
                title_tag = article.select_one('p')
                title = title_tag.get_text(strip = True) if title_tag else ""
                news_dict[topic_jp].append([title, link])

            # Save news_dict into .json
            with open(json_folder_path + "/" + nhk_json, 'w') as file:
                json.dump(news_dict, file, indent = 4)
            
            print(f"> Updated {nhk_json} in {json_folder_path}")
        else:
            print(f"> Could not scrape from '{nhk_url_topic}' ...")


# -------------------------------------------------- #
# Tag filter                                         #
# -------------------------------------------------- #

def filter_attr_href(tag):
    return tag.has_attr('href')