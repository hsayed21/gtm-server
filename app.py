# from pprint import pprint
from pprint import pprint
from flask import Flask, request
from flask_restful import Api
import requests
import pytz
from datetime import datetime
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from github import Github
import json
from bs4 import BeautifulSoup

app = Flask(__name__)
api = Api(app)

# Functions Get Info From IP
def freegeoip_app(ip):
    res = requests.get(
        f"https://api.freegeoip.app/json/{ip}?apikey=578827c0-4829-11ec-ba48-71386ee45891")
    if res.status_code == requests.codes.ok:
        result = res.json()
        result["country"] = result.pop('country_name')
        result["region"] = result.pop('region_name')
        return result
    else:
        return False


def ipapi_co(ip):
    headers = {'User-Agent': 'Mozilla/5.0'}
    res = requests.get(f"https://ipapi.co/{ip}/json/", headers=headers)
    if res.status_code == requests.codes.ok:
        result = res.json()
        result["country"] = result.pop('country_name')
        return result
    else:
        return False


def ip_api_com(ip):
    res = requests.get(f"http://ip-api.com/json/{ip}")
    if res.status_code == requests.codes.ok:
        result = res.json()
        result["region"] = result.pop('regionName')
        result["latitude"] = result.pop('lat')
        result["longitude"] = result.pop('lon')
        return result
    else:
        return False


def ipaddress_my(ip):
    headers = {'User-Agent': 'Mozilla/5.0'}
    payload = {'ip': ip}
    _json = {}
    # session = requests.Session()
    # session.post('https://www.ipaddress.my/',headers=headers,data=payload)
    res = requests.post('https://www.ipaddress.my/',
                        headers=headers, data=payload)
    if res.status_code == requests.codes.ok:
        soup = BeautifulSoup(res.content, "html.parser")
        table_data = soup.findAll("td")
        # print(table_data)
        for element in table_data:
            # if element.get_text() == 'IP Address:':
            # _json["ip_address"] = element.find_next().get_text()
            
            if element.get_text() == 'Hostname:':
                _json["hostname"] = element.find_next().get_text()
            if element.get_text() == 'ISP:':
                _json["isp"] = element.find_next().get_text()
            if element.get_text() == 'City:':
                _json["city"] = element.find_next().get_text()
            if element.get_text() == 'Country:':
                _json["country"] = element.find_next().get_text()
            if element.get_text() == 'State:':
                _json["region"] = element.find_next().get_text()
            if element.get_text() == 'Latitude:':
                _json["latitude"] = element.find_next().get_text()
            if element.get_text() == 'Longitude:':
                _json["longitude"] = element.find_next().get_text()
            if element.get_text() == 'Device:':
                _json["device"] = element.find_next().get_text()
            if element.get_text() == 'Operating System:':
                _json["os"] = element.find_next().get_text()
            if element.get_text() == 'Browser:':
                _json["browser"] = element.find_next().get_text()
                
            # if element.get_text() == 'Time Zone:':
            #     _json["time_zone"] = element.find_next().get_text()
            # if element.get_text() == 'Local Time:':
            #     _json["local_time"] = element.find_next().get_text().strip()
            # if element.get_text() == 'Area Code:':
            #     _json["area_code"] = element.find_next().get_text()
            # if element.get_text() == 'Mobile Brand:':
            #     _json["mobile_brand"] = element.find_next().get_text()

        return _json
    else:
        return False


def final_ip_data(ip):
    result = {}
    if ipaddress_my(ip):
        result = ipaddress_my(ip)
    elif ip_api_com(ip):
        result = ip_api_com(ip)
    elif ipapi_co(ip):
        result = ipapi_co(ip)
    else:
        result = freegeoip_app(ip)

    if "isp" not in result:
        result["isp"] = "None"
    if "hostname" not in result:
        result["hostname"] = "None"
    if "device" not in result:
        result["device"] = "None"
    if "browser" not in result:
        result["browser"] = "None"
    if "os" not in result:
        result["os"] = "None"

    return result


def getDate():
    try:
        res = requests.get(
            "https://worldtimeapi.org/api/timezone/Africa/Cairo")
        iso_date = res.json()['datetime']
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
        replace_text = iso_date[index:].replace(":","")
        new_iso_date = iso_date.replace(iso_date[index:], replace_text)
        format_date = datetime.strptime(new_iso_date, "%Y-%m-%dT%H:%M:%S.%f%z")
        date = format_date.strftime("%Y-%m-%d %I:%M:%S %p")
        return date


'''
def getIP_Fun():
    try:
        res = requests.get("https://api.ipify.org")
        return res.text
    except requests.exceptions.RequestException as e:  # This is the correct syntax
        return "None"
'''



def send_template(_json, _test=False):
    if _test == True:
        return _json
    
    result = '''
    <p>
    <font size="4">
    <font style="background-color: rgb(240, 240, 0);"><strong><font color="#b00000">IP</font>:</font></strong> {0}<br>
    <font style="background-color: rgb(240, 240, 0);"><strong><font color="#b00000">event</font>:</font></strong> <font color="#ffffff" style="background-color: rgb(128, 0, 0);">{1}</font><br>
    <font style="background-color: rgb(240, 240, 0);"><strong><font color="#b00000">page_view_count</font>:</font></strong> {2}<br>
    <font style="background-color: rgb(240, 240, 0);"><strong><font color="#b00000">last_seen</font>:</font></strong> {3}<br>
    <font style="background-color: rgb(240, 240, 0);"><strong><font color="#b00000">country</font>:</font></strong> {4}<br>
    <font style="background-color: rgb(240, 240, 0);"><strong><font color="#b00000">city</font>:</font></strong> {5}<br>
    <font style="background-color: rgb(240, 240, 0);"><strong><font color="#b00000">region</font>:</font></strong> {6}<br>
    <font style="background-color: rgb(240, 240, 0);"><strong><font color="#b00000">latitude</font>:</font></strong> {7}<br>
    <font style="background-color: rgb(240, 240, 0);"><strong><font color="#b00000">longitude</font>:</font></strong> {8}<br>
    <font style="background-color: rgb(240, 240, 0);"><strong><font color="#b00000">isp</font>:</font></strong> {9}<br>
    <font style="background-color: rgb(240, 240, 0);"><strong><font color="#b00000">hostname</font>:</font></strong> {10}<br>
    <font style="background-color: rgb(240, 240, 0);"><strong><font color="#b00000">device</font>:</font></strong> {11}<br>
    <font style="background-color: rgb(240, 240, 0);"><strong><font color="#b00000">os</font>:</font></strong> {12}<br>
    <font style="background-color: rgb(240, 240, 0);"><strong><font color="#b00000">browser</font>:</font></strong> {13}<br>
    </font>
    </p>
    '''.format(_json['IP'], _json['event'], _json['page_view_count'], _json['timestamp'][0], _json['country'], _json['city'], _json['region'], _json['latitude'], _json['longitude'], _json['isp'], _json['hostname'], _json['device'], _json['os'], _json['browser'])
    return result

def send(_json, _test=False):
    # using SendGrid's Python Library
    message = Mail(
        from_email='fromMail@gmail.com',
        to_emails='toMail@gmail.com',
        subject='Track Resume',
        html_content= send_template(_json,_test))
    try:
        sg = SendGridAPIClient("<sendGrid-APi-key>")
        response = sg.send(message)
        return json.dumps(True)
    except Exception as e:
        print(e.message)
        return json.dumps(False)


@app.route('/test_mail', methods=['GET'])
def test_mail():
    send("for testing", True)
    return json.dumps(True)
    
@app.route('/update', methods=['GET'])
def update():
    try:
        g = Github("<github-token>")
        repo = g.get_user().get_repo("gtm-json")
        file_content = repo.get_contents("data.json")
        clear_data_from_github = file_content.decoded_content.decode()
        data_json = json.loads(clear_data_from_github)
        
        
        if request.args.get("ip"):
            getIP = request.args.get("ip")
        else:
            return json.dumps(False)
        
        ip_info = final_ip_data(getIP)
        date_now = getDate()
        
        if request.args.get("event"):
            event = request.args.get("event")
        else:
            event = "Resume Page View"
        
        if "page_url" in data_json or "page_url" not in data_json:
            data_json['page_url'] = "https://test.github.io/resume/"

        if "page_view_count" in data_json:
            data_json['page_view_count'] += 1
        else:
            data_json['page_view_count'] = 1

        if "last_seen" in data_json or "last_seen" not in data_json:
            data_json['last_seen'] = date_now

        ###########################################################
        if "dataSet" in data_json:
            for data in data_json['dataSet']:
                if (getIP == data["IP"]):
                    
                    if "event" in data or "event" not in data:
                        data['event'] = event
                        
                    if "page_view_count" in data:
                        data["page_view_count"] += 1
                    else:
                        data['page_view_count'] = 1

                    if "timestamp" in data:
                        data['timestamp'].insert(0, date_now)
                    else:
                        data['timestamp'] = [date_now]

                    if "country" in data or "country" not in data:
                        data['country'] = ip_info["country"]

                    if "city" in data or "city" not in data:
                        data['city'] = ip_info["city"]

                    if "region" in data or "region" not in data:
                        data['region'] = ip_info["region"]

                    if "latitude" in data or "latitude" not in data:
                        data['latitude'] = ip_info["latitude"]

                    if "longitude" in data or "longitude" not in data:
                        data['longitude'] = ip_info["longitude"]

                    if "isp" in ip_info:
                        data['isp'] = ip_info["isp"]

                    if "hostname" in ip_info:
                        data['hostname'] = ip_info["hostname"]
                        
                    if "device" in ip_info:
                        data['device'] = ip_info["device"]

                    if "os" in ip_info:
                        data['os'] = ip_info["os"]
                    
                    if "browser" in ip_info:
                        data['browser'] = ip_info["browser"]

                    data_json['dataSet'].insert(0, data_json['dataSet'].pop(data_json['dataSet'].index(data)))
                    
                    # send data to gmail using sendgrid
                    send(data)
                    break
            else:
                new_object = {
                    "IP": getIP,
                    "event": event,
                    "page_view_count": 1,
                    "timestamp": [date_now],
                    "country": ip_info["country"],
                    "city": ip_info["city"],
                    "region": ip_info["region"],
                    "latitude": ip_info["latitude"],
                    "longitude": ip_info["longitude"],
                    "isp": ip_info["isp"],
                    "hostname": ip_info["hostname"],
                    "device": ip_info["device"],
                    "os": ip_info["os"],
                    "browser": ip_info["browser"]
                }
                data_json['dataSet'].insert(0, new_object)
                
                # send data to gmail using sendgrid
                send(new_object)
        else:
            new_object = {
                "IP": getIP,
                "event": event,
                "page_view_count": 1,
                "timestamp": [date_now],
                "country": ip_info["country"],
                "city": ip_info["city"],
                "region": ip_info["region"],
                "latitude": ip_info["latitude"],
                "longitude": ip_info["longitude"],
                "isp": ip_info["isp"],
                "hostname": ip_info["hostname"],
                "device": ip_info["device"],
                "os": ip_info["os"],
                "browser": ip_info["browser"]
            }
            data_json['dataSet'] = [new_object]
            # send data to gmail using sendgrid
            send(new_object)

        data_jsonify = json.dumps(data_json, indent=4)
        repo.update_file(path=file_content.path,message="Last Update: {}".format(date_now),content="{}".format(data_jsonify),sha=file_content.sha, branch='master')
        return json.dumps(True)
    except Exception as e:
        # return e.message
        return json.dumps(False)

@app.route('/', methods=['GET'])
def get():
    return {'message': 'Good Day :)'}


if __name__ == '__main__':
    app.run(debug=True)
