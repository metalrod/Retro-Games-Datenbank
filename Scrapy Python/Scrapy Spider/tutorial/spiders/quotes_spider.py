import scrapy
# Einzelne Libaries werden importiert
from scrapy.selector import Selector
# um aus der HTML Einträge zu selektieren
from scrapy.http import HtmlResponse
# zur Kommunikation mit der Internetseite
from scrapy.contrib.loader import ItemLoader

#Hier wurde eine eigene Item Klasse erstellt die unterschiedliche Felder besitzt zum Abspeichern der
#ausgewählten Seiten Daten
class LemonamigaItems(scrapy.Item):
    titel = scrapy.Field()
    genre = scrapy.Field()
    year = scrapy.Field()
    developer = scrapy.Field()
    players = scrapy.Field()
    review = scrapy.Field() #empty
    hardware = scrapy.Field()
    disks = scrapy.Field()
    language = scrapy.Field()
    thumbnail = scrapy.Field()
    date_added = scrapy.Field()

#Der Spider der aufgerufen wird mit dem passenden Namen Lemonamiga_games
class QuotesSpider(scrapy.Spider):
    name = "lemonamiga_games"

    #in Python werden die Funtkionen durch def erstellt
    #hier werden die Seiten von Lemonamiga über eine For Schleife abgelaufen
    #jeder Seitenaufruf geht in den Parser sammelt die Daten und wandert dann weiter in die Pipe
    def start_requests(self):
        urls = ['http://www.lemonamiga.com/games/details.php?id=' + str(i) for i in range(1, 4307)] #1 bis 4307 leider mit Doppelungen
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    # Jeder Request erstellt ein Item und befüllt Ihn mit Daten
    def parse(self, response):

        item = LemonamigaItems()
        #Ausgewählte Erklärung der Syntax
        #der Titel steckt in der HTML in einem Text nach der class mit der Bezeichnung "textGameHeader"
        #es wird bis zum tag font vorgesprungen und der Text extrahiert
        #das wird dann in LemonamigaItems im Feld Titel gespeichert.
        item['titel'] = response.xpath("//strong[@class='textGameHeader']/font/text()").extract()
        item['genre'] = response.xpath("//text()[contains(.,'Genre:')]/../following-sibling::td/a/text()").extract()
        item['year'] = response.xpath("//a[contains(@href,'year')]/strong/font/text()").extract()
        #Hier enthält der Fließtext das Wort "Developer:" und über following-sibling wird nach der Form td/a gesucht und der enthaltende Text
        #extrahiert.
        item['developer'] = response.xpath("//text()[contains(.,'Developer:')]/../following-sibling::td/a/text()").extract()
        item['players'] = response.xpath("//text()[contains(.,'Players:')]/../following-sibling::td/a/text()").extract()
        #item['review'] = response.xpath("//text()[contains(.,'Developer:')]/../following-sibling::td/a/text()").extract() # empty
        item['hardware'] = response.xpath("//text()[contains(.,'Hardware:')]/../following-sibling::td/a/text()").extract()
        item['disks'] = response.xpath("//text()[contains(.,'Disks:')]/../following-sibling::td/a/text()").extract()
        item['language'] = response.xpath("//text()[contains(.,'Language:')]/../following-sibling::td/a/text()").extract()
        #hier steckt die Information im @src Links der Image Datei
        item['thumbnail'] = response.xpath("//img[contains(@src,'/games/screenshots')]/@src").extract()
        item['date_added'] = response.xpath("//a[contains(@href,'date')]/text()").extract()


        #uber yield (ähnlich wie Return, bloß es wird nicht weiter vorgehalten und nach Übergabe gelöscht
        yield item

