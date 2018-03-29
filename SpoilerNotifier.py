import sys
from lxml import html
import requests
import urllib3

mainSite = 'http://mythicspoiler.com/'
def main():


    page = requests.get(mainSite + 'newspoilers.html')
    pageTree = html.fromstring(page.content)

    cards = pageTree.xpath('//img[contains(@src,\'/cards/\')]/@src')

    print(len(cards))

    for card in cards:

        print("Getting " + mainSite + card)
        response = requests.get(mainSite + card)
        if response.status_code == 200:
            with open("1.jpg", "wb") as imageFile:
                imageFile.write(response.content)
        print(card)
        break

    print("Hello world!")


main()