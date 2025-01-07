import requests 

def request_di_values(ip, cookie):
    url = f'http://{ip}/di_value/slot_0'
    headers = {'Cookie': f'{cookie["name"]}={cookie["value"]}'}
    response = requests.get(url, headers=headers)
    return response

