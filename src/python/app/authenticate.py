import requests 
import hashlib
from bs4 import BeautifulSoup


def get_cookie(ip):
    username="root"
    password="00000000"
    url = f"http://{ip}/config"
    hash_output = ""
    try:
        response = requests.get(url)
    except Exception as e:
        return { "error": f'Timeout when fetching http://{ip}/config', "value" : None }
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
            return { "error": "Seeddata not found in the response.", "value" : None }
    else:
        return { "error": f'Error: got response status {response.status_code} when fetching http://{ip}/config', "value" : None }

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
        try:
            response = requests.post(login_url, data=data, headers=headers)
        except Exception as e:
            return { "error": "Timeout when requesting cookie", "value" : None }
        if response.status_code == 200:
            content_type = response.headers.get("Content-Type", "")
            html_response = response.text
            cookies = response.cookies
            for cookie in cookies:
                cookie_name = cookie.name
                cookie_value = cookie.value
        else:
            return { "error": f'response status: {response.status_code}', "value" : None }
    else:
        return { "error": "could not create hash", "value" : None }
    return { "error": None, "value" : cookie_value }

