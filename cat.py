import json
import requests
from time import sleep
from tqdm import tqdm


class YandexDiscAPI:

    def __init__(self, token):
        self.headers = {
            'Authorization': f'OAuth {token}'
        }

    def create_folder(self):
        """Creates folder on Yandex.Disk"""
        url = 'https://cloud-api.yandex.net/v1/disk/resources'
        params = {
            'path': 'PD-132'
        }
        response = requests.put(url, headers=self.headers, params=params)
        if response.status_code in [201, 409]:
            return response.status_code
        else:
            print(f'Произошла ошибка при создании папки: {response.text}')
            return None

    def get_url_image(self, text_on_image='Hello'):
        """
        Gets a link to download an image using an API request
        (default "Hello")
        """
        url = 'https://cataas.com/cat/says/'
        params = {
            'json': True
        }
        response = requests.get(url + text_on_image, params=params)
        if response.status_code == 200:
            return response.json()['url']
        else:
            print(f'Произошла ошибка при получении картинки: {response.text}')
            return None

    def upload_image_on_ydisk(self, name_image='Hello'):
        """Uploads a picture to Yandex.Disk."""
        url = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
        params = {
            'url': f'{self.get_url_image(name_image)}',
            'path': f'PD-132/{name_image}'
        }
        response = requests.post(url, headers=self.headers, params=params)
        if response.status_code == 202:
            operations_id = (response.json()['href'].split('/')[-1])
            for load_file in tqdm(range(1)):
                self.get_operation_status(operations_id)
            return
        else:
            print(f'Ошибка загрузки файла {response.text}')
            return None

    def get_operation_status(self, operations_id):
        """Checks the file upload status"""
        url = "https://cloud-api.yandex.net/v1/disk/operations/"
        count = 3
        while count > 0:
            response = requests.get(url + operations_id, headers=self.headers)
            if response.json()['status'] == 'in-progress':
                sleep(3)
                count -= 1
            elif response.json()['status'] == 'success':
                print(f'Файл загружен успешно!')
                return
            else:
                print(f'Ошибка загрузки файла {response.text}')
                return None
        else:
            print(f'Превышено время ожидания загрузки файла')
            return None

    def get_json_file(self):
        """Saves file information (name, size) from Yandex.Disk to a json file"""
        url = 'https://cloud-api.yandex.net/v1/disk/resources'
        params = {
            'path': 'PD-132',
            'fields': '_embedded.items.name, _embedded.items.size'
        }
        response = requests.get(url, headers=self.headers, params=params)
        content_on_folder = response.json()['_embedded']['items']
        with open('images_info.json', 'w', encoding='utf-8') as f:
            json.dump(content_on_folder, f, indent=2, ensure_ascii=False)
        print(f'Информация сохранена в images_info.json')
        return


text = input('Введите текст для картинки: ')
token = input("Введите токен Яндекс.Диска: ")
yd_api = YandexDiscAPI(token)
yd_api.create_folder()
yd_api.upload_image_on_ydisk(text)
yd_api.get_json_file()