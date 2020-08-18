import datetime


def getDate(delta=1):
    today = datetime.datetime.today()
    yesterday = today - datetime.timedelta(delta)
    return yesterday.strftime("%m-%d-%Y")
