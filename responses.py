import get_lost_sector


def handle_response(message) -> str:
    lower_message = message.lower()
    print("MADE IT TO CAYDE RESPONSES")
    if lower_message[:5] == 'cayde':

        if lower_message[5:] == ' lost sector':  # lower_message[5:] == ' lost sector':
            lost_sector_cache = []
            if not lost_sector_cache:  # if there is no data in cache
                data = get_lost_sector.get_lost_sector_rewards()  # [prefix, message, postfix, items_dictionary]
                lost_sector_cache = data
            else:  # there is data in the cache, return this data
                data = lost_sector_cache

            items_dictionary = data[3]
            prefix = data[0]
            message1 = data[1]
            postfix = data[2]

            print("MADE IT TO LOWER MESSAGE BLOCK")
            dictionaryString = ""

            for item in items_dictionary:
                dictionaryString = dictionaryString + "{} \n{} \n \n".format(item, items_dictionary[item][0])

            dictionaryString = dictionaryString + '\n'

            print(prefix + "\n" + message1 + "\n" + dictionaryString + postfix)
            return message1 + "\n" + "The items you can get from it are:" + "\n" + dictionaryString + postfix

        elif lower_message[5:] == ' help':
            print("cayde helpful message")
            return 'Hello, you can call me by typing "cayde" or tell me to do something by typing "cayde **insert command**"\n\nMy functionality is limited to:\n"cayde **lost sector**": Returns updated information on location of lost sector and rewards\n"cayde **hello/hi**": I will respond accordingly\n"cayde **help**": This extremely helpful message\n'

        elif lower_message[5:] == ' hello' or lower_message[6:] == ' hi':
            return "Hey there, I'm Cayde!"

        elif lower_message[5:] == ' tell germy hes lame':
            return "u lame Germy"

        #else:
        #    return 'Hello, I am Cayde-7. I was created solely for purpose of retrieving the daily lost sector location and rewards data for my owner @kibi#8987 please direct any questions/feedback to him.'
