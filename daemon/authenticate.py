import requests 
import hashlib
from bs4 import BeautifulSoup


def get_cookie(url="http://10.0.0.3/config",username="root",password="00000000"):
    hash_output = ""
    print(f'getting cookie for {url}')
    response = requests.get(url)
    if response.status_code == 200:
        content_type = response.headers.get("Content-Type", "")
        html_response = response.text
        soup = BeautifulSoup(html_response, 'html.parser')
        seeddata_input = soup.find('input', {'name': 'seeddata'})
        if seeddata_input:
            seeddata_value = seeddata_input['value']
            hash_input =  f"{seeddata_value}:{username}:{password}"
            hash_output = hashlib.md5(hash_input.encode()).hexdigest()
        else:
            return { "error": "Seeddata not found in the response.", "result" : None }
    else:
        return { "error": "Failed to retrieve data", "result" : None }

    cookie_name = ""
    cookie_value = ""
    login_url = url + "/index.html"
    if len(hash_output) > 1:
        data = {
            "seeddata": seeddata_value,
            "authdata": hash_output
        }
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        response = requests.post(login_url, data=data, headers=headers)
        if response.status_code == 200:
            content_type = response.headers.get("Content-Type", "")
            html_response = response.text
            cookies = response.cookies
            for cookie in cookies:
                cookie_name = cookie.name
                cookie_value = cookie.value
        else:
            return { "error": "Failed to retrieve data", "result" : None }
    else:
        return { "error": "could not create hash", "result" : None }
    result = { "name" : cookie_name, "value" : cookie_value }
    return { "error": None, "result" : result }



    #response2 = requests.get(url2, cookies=cookies)

def get_cookies(devices):
    device_cookies = []
    for device in devices:
        url = f"http://{device}/config"
        cookie_obj = get_cookie(url)
        device_cookies.append({ "ip" : device, "cookie" : cookie_obj })
    return device_cookies
