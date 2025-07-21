import json
import requests
import time

def create_folder(token):
    """Creates a "PD-132" folder on Yandex.Disk"""
    url = 'https://cloud-api.yandex.net/v1/disk/resources'
    headers = {
        'Authorization': f'OAuth {token}'
    }
    params = {
        'path': 'PD-132'
    }
    response = requests.put(url, headers=headers, params=params)
    if response.status_code in [201, 409]:
        return response.status_code
    else:
        print(f"Произошла ошибка при создании папки: {response.text}")
        return None

def get_url_image(text_on_image):
    """gets a link to download an image using an API request"""
    if text_on_image == "":
        text_on_image = "Hello"
    url = 'https://cataas.com/cat/says/'
    params = {
        'json': True
    }
    response = requests.get(url + text_on_image, params=params)
    if response.status_code == 200:
        return response.json()['url']
    else:
        print(f"Произошла ошибка при получении картинки: {response.text}")
        return None

def upload_image_on_ydisk(token, text_on_image):
    """
    Uploads a picture to Yandex.Disk.
    Returns the ID of this operation.
    """
    url = "https://cloud-api.yandex.net/v1/disk/resources/upload"
    headers = {
        'Authorization': f'OAuth {token}'
    }
    params = {
        'url': f'{get_url_image(text_on_image)}',
        'path': f'PD-132/{text_on_image}'
    }
    response = requests.post(url, headers=headers, params=params)
    if response.status_code == 202:
        operations_id = (response.json()['href'].split('/')[-1])
        return operations_id
    else:
        print(f'Ошибка загрузки файла {response.text}')
        return None

def get_operation_status(token, operations_id):
    """Checks the file upload status"""
    url = "https://cloud-api.yandex.net/v1/disk/operations/"
    headers = {
        'Authorization': f'OAuth {token}'
    }
    count = 3
    while count > 0:
        response = requests.get(url + operations_id, headers=headers)
        if response.json()['status'] == 'in-progress':
            print(f'Производится загрузка файла {"..."*(4 - count)}')
            time.sleep(3)
            count -= 1
        elif response.json()['status'] == 'success':
            return print(f'Файл загружен успешно!')
        else:
            return print(f'Ошибка загрузки файла {response.text}')
    else:
        return print(f'Превышено время ожидания загрузки файла')

def get_json_file(token):
    """Saves file information (name, size) from Yandex.Disk to a json file"""
    url = 'https://cloud-api.yandex.net/v1/disk/resources'
    headers = {
        'Authorization': f'OAuth {token}'
    }
    params = {
        'path': 'PD-132',
        'fields': '_embedded.items.name, _embedded.items.size'
    }
    response = requests.get(url, headers=headers, params=params)
    content_on_folder = response.json()['_embedded']['items']
    with open('images_info.json', 'w', encoding='utf-8') as f:
        json.dump(content_on_folder, f,indent=2)
    return print(f'Информация сохранена в images_info.json')

token = input("Введите токен Яндекс.Диска: ")
text_on_image = input('Введите текст для картинки: ')
create_folder(token)
operations_id = upload_image_on_ydisk(token, text_on_image)
get_operation_status(token, operations_id)
get_json_file(token)