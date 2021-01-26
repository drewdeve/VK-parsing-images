from requests import post


class Auth:

    @staticmethod
    def get_token(login: str, password: str) -> str:
        data = {
            'grant_type': 'password',
            'client_id': '2274003',
            'client_secret': 'hHbZxrka2uZ6jB1inYsH',
            'v': 5.103,
            'username': login,
            'password': password
        }
        request = post('https://oauth.vk.com/token', params=data)
        json = request.json()
        return '' if 'error' in json else json['access_token']
