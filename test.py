from datetime import datetime
import requests
import pytz
iso_date = "2021-11-18T16:31:17.602925+02:00"
format_date = datetime.strptime(iso_date, "%Y-%m-%dT%H:%M:%S.%f%z")
date = format_date.strftime("%Y-%m-%d %I:%M:%S %p")
tz = pytz.timezone('Africa/Cairo')
current_date = datetime.now(tz)
asd = current_date.isoformat()
print(asd)
def getDate():
    try:
        res = requests.get(
            "https://worldtimeapi.org/api/timezone/Africa/Cairo")
        iso_date = str(res.json()['datetime'])
        index = iso_date.index("+")
        replace_text = iso_date[index:].replace(":","")
        new_iso_date = iso_date.replace(iso_date[index:], replace_text)
        format_date = datetime.strptime(new_iso_date, "%Y-%m-%dT%H:%M:%S.%f%z")
        date = format_date.strftime("%Y-%m-%d %I:%M:%S %p")
        return date
    except requests.exceptions.RequestException as e:  # This is the correct syntax
        tz = pytz.timezone('Africa/Cairo')
        current_date = datetime.now(tz)
        iso_date = current_date.isoformat()
        index = iso_date.index("+")
        sub_ = iso_date[index:len(iso_date)] .replace(":","")
        sub = iso_date.replace(iso_date[index:len(iso_date)],sub_)
        print(sub)
        # format_date = datetime.strptime(iso_date, "%Y-%m-%dT%H:%M:%S.%f%z")
        # date = format_date.strftime("%Y-%m-%d %I:%M:%S %p")
        # return date



