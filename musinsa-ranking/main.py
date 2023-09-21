import os
from smtp import Smtp
from ranking import MusinsaRanking

if __name__ == '__main__':
    url = "https://search.musinsa.com/ranking/keyword"
    sender = os.environ['EMAIL_ADDRESS_FROM']
    sender_pw = os.environ['EMAIL_PW']
    receiver = os.environ['EMAIL_ADDRESS_TO']

    smtp = Smtp(sender, sender_pw)
    ranking = MusinsaRanking(url).get_ranking()
    smtp.send_mail(receiver, ranking)
