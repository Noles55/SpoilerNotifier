from lxml import html
import requests
import time
import os
import re

mainSite = 'http://mythicspoiler.com/'
botId = os.environ['BOT_ID']
threshold = 40
sleepTime = 5

def main():

    firstLoop = True

    while True:

        if not firstLoop:
            time.sleep(60 * sleepTime)

        firstLoop = False

        # Get the newest spoilers page
        page = requests.get(mainSite + 'newspoilers.html')

        # Get the page tree from the page contents
        pageTree = html.fromstring(page.content)

        # Find all card images
        allCards = pageTree.xpath('//img[contains(@src,\'/cards/\')]/@src')

        # Get the last card spoiled from previous post
        lastCardFile = open("LastCard.txt", 'r')
        lastCard = lastCardFile.readline()

        # List for new cards to post
        cardsToSpoil = list()


        # Add the card paths to the cardsToSpoil list, stopping once we reach the last card spoiled from the previous post
        for card in allCards:

            if lastCard in card:
                break

            cardsToSpoil.append(card)

        # Write to the last card file with the newest, most recent card, since we don't want to post it again
        lastCardFile.close()
        if len(cardsToSpoil) == 0:
           continue
        elif len(cardsToSpoil) > threshold:
            postHeaders = {'Content-Type': 'application/json', }
            postData = '{"bot_id" : "' + botId + '", "text" : "More than ' + str(threshold) + ' new spoilers!"'
            response = requests.post('https://api.groupme.com/v3/bots/post', headers=postHeaders, data=postData)
            writeLastCard(cardsToSpoil[0])
            continue

        writeLastCard(cardsToSpoil[0])

        # Retrieve each card image and post it to GroupMe via the bot
        for card in cardsToSpoil:

            time.sleep(2)

            print("Posting " + mainSite + card)

            cardLink = re.search('(.*/[^.[0-9]+)[0-9]*.jpg', card)
            cardLink = mainSite + cardLink.group(1) + ".html"
            # Get the card image data
            response = requests.get(mainSite + card)
            if response.status_code != 200:
                print("Failed to get card image data")
                continue

            # Post the image data to the GroupMe Image
            imageHeaders = {'X-Access-Token' : os.environ['ACCESS_TOKEN'], 'Content-Type' : 'image/jpeg'}
            imageData = response.content
            response = requests.post('https://image.groupme.com/pictures', data=imageData, headers=imageHeaders)

            if response.status_code != 200:
                print("Failed to post image data to GroupMe image service")
                continue

            # Extract the image url from the response
            responseText = response.text
            imageURL = re.search('.url\":\"([^"]+)', responseText)
            imageURL = imageURL.group(1)

            # Post the image to the GroupMe chat
            postHeaders = {'Content-Type' : 'application/json',}
            postData = '{"bot_id" : "' + botId + '", "text" : "' + cardLink + \
                       '", "attachments" : [ { "type" : "image", "url" : "' + imageURL + '"} ] }'
            response = requests.post('https://api.groupme.com/v3/bots/post', headers=postHeaders, data=postData)




def writeLastCard(card):
    lastCardFile = open("LastCard.txt", 'w')
    cardRegex = re.search('/cards/(.*[^0-9])[0-9]*\..+', card)
    lastCardFile.write(cardRegex.group(1))
    lastCardFile.close()


main()