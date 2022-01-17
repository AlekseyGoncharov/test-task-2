import requests

def test_blacklist():
    global exit_code
    test_ip = "10.0.45.45"
    ip_headers = {"X-Forwarded-For": test_ip}
    url = "{}/blacklisted".format(app_url)
    r = requests.get(url, headers=ip_headers)
    code = r.status_code
    if code != 444:
        print("We don't receive 444 in blacklisted")
    else:
        print("444 Received")
    url_list = "{}/list_blacklist".format(app_url)
    r = requests.get(url_list, headers=ip_headers)
    code = r.status_code
    if code != 403:
        print("IP didn't blocked")
        exit_code = 1
    else:
        print("IP has been banned")
    r = requests.get(url_list)
    data = r.json()
    found = False
    for record in data:
        if test_ip in record["ip"]:
            found = True
    if not found:
        print("blocked IP didn't found in database")
        exit_code = 1
    else:
        print("record in db was created")
    url = "{}/unban/?ip={}".format(app_url, test_ip)
    r = requests.get(url)
    r.raise_for_status()
    r = requests.get(url_list)
    data = r.json()
    for record in data:
        if test_ip in record["ip"]:
            print("Ip wasn't deleted from database")
            exit_code = 1
        else:
            print("IP removed from database")
    return 0

def test_1():
    global exit_code
    test_numbers = [12, 6, 100]
    for i in test_numbers:
        url = "{}/?{}=test".format(app_url, str(i))
        r = requests.get(url)
        result = r.json().get("Result")
        if result != i*i:
            print("Unexpected result, should be: {}, got: {}".format(i*i, result))
            exit_code = 1
        else:
            print("Result is right! Congratulation")
    return 0

app_url = "http://127.0.0.1:7090"
exit_code = 0
test_blacklist()
test_1()
exit(exit_code)
