"""
Ebay finding Script
Diese Script sucht mit Hilfe der Ebay API nach Amiga Spiele Auktionen.
Idealer Weise läuft es als Backend Service und wird in regelmäßigen Abständen ausgeführt.
"""

import datetime
import mysql.connector as mysql
from ebaysdk.finding import Connection as finding
from ebaysdk.soa.finditem import Connection as FindItem
from ebaysdk.exception import ConnectionError

import json
import re

def get_auction_status(auctionid):
    api = FindItem(domain='svcs.ebay.com',
                   consumer_id='ErikDlli-Datenban-PRD-160b6dcaa-2dcc188c',
                   appid='ErikDlli-Datenban-PRD-160b6dcaa-2dcc188c',
                   siteid='EBAY-DE',
                   config_file=None,)
    records = api.find_items_by_ids([auctionid[0]])
    return records

def find_auctions(ebay, game):
    new_auctions_list = list()
    game_title = re.sub(r'\W+', ' ', game[0])
    keywords = u'Amiga {title}'.format(title=str(game_title))
    request = {'keywords': keywords,
               'categoryID': '139973',}
    response = ebay.execute('findItemsAdvanced', request)
    json_resp = json.loads(response.json())
    if json_resp['searchResult']['_count'] == '0':
        print("No auctions found for {}".format(game_title))
        print("Keywords: {}".format(keywords))
    else:
        items = json_resp['searchResult']['item']
        for item in items:
            if item['primaryCategory']['categoryId'] == '139973':
                auction_item = (game_title,
                           item['itemId'],
                           item['title'],
                           item['sellingStatus']['currentPrice']['value'],
                           item['location'],
                           item['viewItemURL'],
                           item['sellingStatus']['sellingState'],
                           datetime.datetime.strptime(item['listingInfo']['endTime'], '%Y-%m-%dT%H:%M:%S.%fZ'))
                new_auctions_list.append(auction_item)
    return new_auctions_list


if __name__ == "__main__":
    print_label = "### => {}"
    print(print_label.format("Start"))

    # Connect to database
    try:
        # security issue 1
        DB_CON = mysql.connect(host="127.0.0.1", user="root", passwd="nab556", database="Amiga")
        print(print_label.format("Database connected"))
    except mysql.errors.Error as e:
        print(e.msg)
    CURSOR = DB_CON.cursor()

    # ebay sdk instance
    try:
        # security issue 2
        EBAY_API = finding(domain='svcs.ebay.com',
                           appid='ErikDlli-Datenban-PRD-160b6dcaa-2dcc188c',
                           siteid='EBAY-DE',
                           config_file=None,
                           warnings=True)
        print(print_label.format("Ebay connected"))
    except ConnectionError as ce:
        print(ce)

    # SERVICE UNAVAILEBLE SINCE Nov 2018
    # update completed auctions
    # CURSOR.execute("SELECT AUCTIONID FROM EBAY WHERE ENDTIME < NOW() ")
    # try:
    #     result = CURSOR.fetchall()
    # except mysql.InterfaceError:
    #     result = list()
    # itemIDs = [n[0] for n in result]
    # items = get_auction_status(itemIDs)
    # print(items)

    CURSOR.execute("UPDATE EBAY SET STAT = 'Inactive' WHERE ENDTIME < NOW() ")
    print(print_label.format("{} were set to inactive".format(CURSOR.rowcount)))



    # Get list of Games from database
    list_games = list()
    CURSOR.execute("SELECT title, developer, hardware, language FROM LEMONAMIGA")
    result = CURSOR.fetchall()
    for i in result:
        game = (i[0], i[1], i[2], i[3])
        if not list_games.__contains__(game):
            list_games.append(game)

    # Get ebay auctions

    # Insert auctions into Database
    sql_insert = "REPLACE INTO EBAY (GAMETITLE, AUCTIONID, AUCTIONTITLE,PRICE,LOCATION,URL,STAT,ENDTIME) VALUES (%s, %s, %s, %s , %s, %s, %s, %s )"
    for game in list_games:
        new_auction_list = find_auctions(EBAY_API, game)
        if new_auction_list.__len__() > 0:
            CURSOR.executemany(sql_insert, new_auction_list)
            DB_CON.commit()
            print(CURSOR.rowcount, "was inserted")

    DB_CON.disconnect()
    print(print_label.format("Finish"))
