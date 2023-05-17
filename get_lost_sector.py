import time
import requests
import collections

collections.Callable = collections.abc.Callable
from bs4 import BeautifulSoup


def get_lost_sector_rewards() -> list:
    vgm_url = 'https://todayindestiny.com/'

    html_text = requests.get(vgm_url).text
    soup = BeautifulSoup(html_text, 'html.parser')

    # find the parent div of a p tag that contains the word "Reward" and "Lost Sector" in its text field
    lostSectorDiv = soup.select_one('div[id*="lost_sector_lost_sector_"]')
    lostSectorRewardsDiv = soup.select_one('p:-soup-contains("Reward")').parent
    lostSectorDivEventCardHeaderText = soup.select_one('p:-soup-contains("Lost Sector")').parent
    lostSectorDivEventCardDescription = soup.select_one('div:-soup-contains("Master Difficulty:")')

    lostSectorDivSoup = BeautifulSoup(str(lostSectorDiv), 'html.parser')
    masterDifficultyDiv = lostSectorDiv.find('div', {"class": "eventCardDescription"})

    # find location (planet it is on) of lost sector
    exclusionText = "\n"
    locationOfLostSector = str(masterDifficultyDiv.text)
    locationOfLostSector = locationOfLostSector[0:locationOfLostSector.find(exclusionText)].strip()

    # find name of lost sector
    lostSectorName = lostSectorDivEventCardHeaderText.find('p', {"class": "eventCardHeaderName"}).text

    # create dict for todays items
    items_dictionary = {}

    # loop through divs with class "renderDisplayCardSection_DatabaseItems_ManifestItemContainer"
    for div in lostSectorRewardsDiv.select('div.renderDisplayCardSection_DatabaseItems_ManifestItemContainer'):
        itemID = div.find('div', {"class": "manifest_item_container InventoryItem_container"}).get("id")[23:]
        itemName = div.find('div', {"class": "manifest_item_tooltip_name"}).text
        items_dictionary[itemName] = ["<https://www.light.gg/db/items/{}>".format(str(itemID)), itemID]

    prefix = '''Hello, I am Cayde-7. I was created solely for purpose of retrieving the daily lost sector location and rewards data.
    '''

    message = '''Today's lost sector is {} on {}
    '''.format(lostSectorName, locationOfLostSector)

    postfix = '''I will return tomorrow when there is a new daily lost sector. Have a good day
    '''

    # print(items_dictionary)
    # print(prefix)
    # print(message)
    # for item in items_dictionary:
    #     print("{} \n{}".format(item, items_dictionary[item][0]))
    #     time.sleep(0.25)
    # print(postfix)

    return [prefix, message, postfix, items_dictionary]
