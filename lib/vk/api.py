import time
import requests
from lib.util.dotdict import DotDict


class VkApiError(BaseException):
    pass


class Api:

    def __init__(self, access_token: str):
        self.access_token = access_token
        self.version = 5.103
        self.session = requests.session()
        self.last_request = 0
        self.delay = 1

    def get_posts(self, owner_id: int, count: int = 3) -> list:
        request = self.method('wall.get', {'owner_id': owner_id, 'count': count})
        return request['items']

    def method(self, method: str, values: dict = None):
        if values is None:
            values = {}
        default = {
            'access_token': self.access_token,
            'v': self.version
        }
        data = {**values, **default}
        headers = {
            'User-Agent': 'VKAndroidApp/5.48-4286 (1; 1; 1; 1; 1; 1)',
        }
        if (diff := time.time() - self.last_request) < self.delay:
            time.sleep(self.delay - diff)
        request = self.session.post('https://api.vk.com/method/' + method, data=data, headers=headers)
        self.last_request = time.time()
        json = DotDict(request.json())
        if 'error' in json:
            error = json.error
            raise VkApiError(error)
        return json.response
