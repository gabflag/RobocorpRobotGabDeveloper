from robocorp import browser
from robocorp.tasks import task
from bs4 import BeautifulSoup
import pandas as pd
import requests
import os
import uuid


def CountSearchPhrase(title, description, search_phrase):
    """
    Counts the number of occurrences of a search phrase in the article's title and description.

    Parameters:
        title (str): The title of the article.
        description (str): The description of the article.
        search_phrase (str): The search phrase to count.

    Returns:
        int: The number of occurrences of the search phrase in the title and description.
    """
    combined_text = title + description
    count = combined_text.lower().count(search_phrase.lower())
    return count


def DownloadFile(url, file_path):
    """
    Downloads a file from a given URL and saves it to the specified path.

    Parameters:
        url (str): URL of the file to be downloaded.
        file_path (str): Full path where the downloaded file will be saved.

    Returns:
        None. This function does not return any value.
    """

    response = requests.get(url)
    response.raise_for_status()

    with open(file_path, "wb") as file:
        file.write(response.content)


def GetPublishedData(url):
    """
    Retrieves the publication or last update date from a given URL.

    Parameters:
        url (str): The URL of the publication to be analyzed.

    Returns:
        str: A string representing the publication or last update date extracted from the URL.
        The format of the date will depend on the page content and its structure.
    """
    browser.configure(
        browser_engine="chromium",
        screenshot="only-on-failure",
        headless=True,
    )
    browser.configure_context(ignore_https_errors=True)
    page = browser.context().new_page()
    page.set_default_timeout(120000)
    page.goto(url, wait_until="commit")

    try:
        page.wait_for_timeout(timeout=4000)
        html_content = page.content()
        soup = BeautifulSoup(html_content, "html.parser")

        if "https://apnews.com/projects/" in url:
            article = soup.find("p", attrs={"class": "story-by-copy"})
            date = article.get_text()

        else:
            article = soup.find("div", attrs={"class": "Page-datePublished"})

            if article == None:
                article = soup.find("div", attrs={"class": "Page-dateModified"})

            date = article.find("bsp-timestamp").get("data-timestamp")

    except Exception as e:
        date = None
        print(f"Erro timeout on get article page: {e}")
        page_html = page.content()
        with open("data_log_erro_page.html", "w", encoding="utf-8") as file:
            file.write(page_html)

        print("Page content saved in 'data.html'")
    finally:
        page.close()

    return date


def extract_news_data(page, search_phrase):
    """
    Extracts relevant information from news articles provided in an HTML page.

    Parameters:
        page (str): HTML page in string format containing news articles.
        search_phrase (str): Search term used to filter articles of interest.

    Returns:
        list of dict: A list of dictionaries, where each dictionary contains the following keys:
            'title' (str): Title of the article.
            'date' (str): Date of the article, formatted as a timestamp or in full text, depending on the extraction location.
            'description' (str): Description of the article.
            'link' (str): URL of the article.
            'image_url' (str): URL of the image associated with the article.
            'search_phrase' (str): Search term used to find the article.
            'image_file_path' (str): Local path where the article's image was saved.
    """

    news_data = []
    soup = BeautifulSoup(page, "html.parser")

    articles = soup.find_all(
        "div",
        attrs={
            "data-mobile-alt-layout": "true",
            "data-origintemplate": "PagePromo",
            "class": "PagePromo",
        },
    )

    for article in articles:
        # Extract the title
        title_element = article.find("div", class_="PagePromo-title")
        title = str(title_element.get_text()).replace("\n", " ")
        while "  " in title:
            title = title.replace("  ", " ")

        # Extract the description
        description_element = article.find("div", class_="PagePromo-description")
        description = str(description_element.get_text()).replace("\n", " ")
        while "  " in description:
            description = description.replace("  ", " ")

        # Extract the link
        link_element = article.find("a", class_="Link")
        link = link_element["href"]

        # Extract the image URL
        image_element = article.find("img", class_="Image")
        image_url = image_element["src"]

        # Extract the date
        date = GetPublishedData(link)
        print("date", date)

        file_name = f"{uuid.uuid4().hex}.jpg"
        image_file_path = os.path.join("output", file_name)
        DownloadFile(image_url, image_file_path)

        count = CountSearchPhrase(title, description, search_phrase)

        # Append the extracted data to the news_data list
        news_data.append(
            {
                "title": title,
                "date": date,
                "description": description,
                "link": link,
                "image_url": image_url,
                "search_phrase": search_phrase,
                "appears_of_search_phrase": count,
                "image_file_path": image_file_path,
            }
        )

    return news_data


@task
def solve_challenge():
    """
    Solve the RPA challenge by extracting news data from AP News.
    """

    # Setting the parameters
    search_phrase = "trump and biden"
    # list_category = ['Live Blogs', 'Photo Galleries', 'Sections', 'Stories', 'Subsections', 'Videos', 'Featured Articles']
    list_category = ["Subsections", "Stories"]
    months = 1

    # Browser configuration
    browser.configure(
        browser_engine="chromium",
        screenshot="only-on-failure",
        headless=False,
    )
    browser.configure_context(
        ignore_https_errors=True,
    )
    context = browser.context()
    context.clear_cookies()
    page = context.new_page()
    page.set_default_timeout(60000)

    # Navigating to the search site
    page.goto(f"https://apnews.com/", wait_until="load")

    try:
        page.wait_for_selector(
            selector="#onetrust-accept-btn-handler",
            timeout=60000,
            state="visible",
        )
        page.click("#onetrust-accept-btn-handler")
    except Exception as e:
        print("Cookie handling")
        print(f"ERRO: {e}")

    page.click("button.SearchOverlay-search-button")
    page.wait_for_timeout(timeout=2000)
    page.fill("input.SearchOverlay-search-input", search_phrase)
    page.click("button.SearchOverlay-search-submit")
    page.wait_for_load_state(state="domcontentloaded", timeout=60000)

    # Filters
    page.click("div.SearchResultsModule-filters-content")
    for category in list_category:
        filter_selector = f'//span[contains(text(), "{category}")]'
        try:
            page.wait_for_selector(filter_selector, state="visible", timeout=10000)
            page.click(filter_selector)
        except Exception as e:
            print(f"Unable to click on filter {category}: {e}")

    page.press("div.SearchResultsModule-filters-title", "Enter")

    try:
        page.wait_for_load_state(timeout=100000)
    except Exception as e:
        print(f"Erro timeout on download page: {e}")

    page.wait_for_timeout(timeout=20000)
    html_content = page.content()

    """
    with open('output/search_page.html', 'w', encoding='utf-8') as file:
        file.write(html_content)
    """

    news_data = extract_news_data(html_content, search_phrase)
    df = pd.DataFrame(
        news_data,
        columns=[
            "title",
            "date",
            "description",
            "link",
            "image_url",
            "search_phrase",
            "appears_of_search_phrase",
            "image_file_path",
        ],
    )
    df.to_excel("output/RPAChallengeRobocorp.xlsx", index=False)


# solve_challenge()
