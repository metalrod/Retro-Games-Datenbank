import datetime
import re
import json
from ebaysdk.finding import Connection as finding
from ebaysdk.exception import ConnectionError


class Error(Exception):
    pass


class EbayException(Error):
    def __init__(self, expression, message):
        self.expression = expression
        self.message = message


class Ebay(finding):
    def __init__(self, configfile=None, apiid=None):
        if configfile is None and apiid is None:
            raise EbayException
        self._configfile = configfile
        self._apiid = apiid
        self._auction_list = list()
        try:
            self._ebay = finding(domain='svcs.ebay.com', appid=self._apiid, config_file=self._configfile,
                                 siteid='EBAY-DE', warnings=True)
        except ConnectionError as ce:
            print(ce)

    @property
    def auction_list(self):
        return self._auction_list

    @auction_list.setter
    def find_auctions(self, game):
        new_auctions_list = list()
        if type(game) is str:
            game_title = re.sub(r'\W+', ' ', game)
            keywords = u'Amiga {title}'.format(title=str(game_title))
            request = {'keywords': keywords,
                       'categoryID': '139973',
                       # 'itemFilter': [
                       # {'name' : 'Condition',
                       # 'value' : 'Used'},
                       # {'name' : 'LocatedIn',
                       # 'value' : 'GB'},
                       #    ],
                       # 'affiliate' : {'trackingId' : 1},
                       # 'sortOrder': 'CountryDescending',
                       }
            response = self._ebay.execute('findItemsAdvanced', request)
            json_resp = json.loads(response.json())
            if json_resp['searchResult']['_count'] == '0':
                print("No auctions found for {}".format(game[0]))
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
                                        datetime.datetime.strptime(item['listingInfo']['endTime'],
                                                                   '%Y-%m-%dT%H:%M:%S.%fZ'))
                        new_auctions_list.append(auction_item)
        if type(game) is list(str()):
            for title in game:
                game_title = re.sub(r'\W+', ' ', title)
                keywords = u'Amiga {title}'.format(title=str(game_title))
                request = {'keywords': keywords,
                           'categoryID': '139973',
                           # 'itemFilter': [
                           # {'name' : 'Condition',
                           # 'value' : 'Used'},
                           # {'name' : 'LocatedIn',
                           # 'value' : 'GB'},
                           #    ],
                           # 'affiliate' : {'trackingId' : 1},
                           # 'sortOrder': 'CountryDescending',
                           }
                response = self._ebay.execute('findItemsAdvanced', request)
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
                                            datetime.datetime.strptime(item['listingInfo']['endTime'],
                                                                       '%Y-%m-%dT%H:%M:%S.%fZ'))
                            new_auctions_list.append(auction_item)
        else:
            raise TypeError('game must be str() or list(str())')
        self.auction_list.append(new_auctions_list)
