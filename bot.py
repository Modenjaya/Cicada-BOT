from aiohttp import (
    ClientResponseError,
    ClientSession,
    ClientTimeout
)
from aiohttp_socks import ProxyConnector
from eth_account import Account
from eth_account.messages import encode_defunct
from eth_utils import to_hex
from datetime import datetime, timezone
from colorama import *
import asyncio, random, uuid, json, os, pytz

# Import pustaka Anti-Captcha resmi
from anticaptchaofficial.turnstileproxyless import *

wib = pytz.timezone('Asia/Jakarta')

USER_AGENT = [
  "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
  "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
  "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
  "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
  "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
  "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
  "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
  "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
  "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
  "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
  "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0",
  "Mozilla/5.0 (X11; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0",
  "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
  "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
  "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 OPR/106.0.0.0"
]

class Cicada:
    def __init__(self) -> None:
        self.PRIVY_HEADERS = {}
        self.BASE_HEADERS = {}
        self.PRIVY_API = "https://auth.privy.io"
        self.BASE_API = "https://campaign.cicada.finance/api"
        self.REF_CODE = "ltiM7mZp" # Anda bisa mengubahnya dengan milik Anda.
        self.SITE_KEY = "0x4AAAAAAAM8ceq5KhP1uJBt"
        self.CAPTCHA_KEY = None # Sekarang ini hanya untuk Anti-Captcha
        self.proxies = []
        self.proxy_index = 0
        self.account_proxies = {}
        self.privy_id = {}
        self.access_tokens = {}
        self.identity_tokens = {}
        self.header_cookies = {}

    def clear_terminal(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def log(self, message):
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}{message}",
            flush=True
        )

    def welcome(self):
        print(
            f"""
        {Fore.GREEN + Style.BRIGHT}Auto Claim {Fore.BLUE + Style.BRIGHT}Cicada - BOT
            """
            f"""
        {Fore.GREEN + Style.BRIGHT}Rey? {Fore.YELLOW + Style.BRIGHT}<INI WATERMARK>
            """
        )

    def format_seconds(self, seconds):
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"
    
    # Fungsi ini khusus untuk memuat kunci Anti-Captcha
    def load_anticaptcha_key(self):
        try:
            with open("anticaptcha_key.txt", 'r') as file:
                captcha_key = file.read().strip()
                self.log(f"{Fore.GREEN + Style.BRIGHT}Menggunakan kunci Anti-Captcha dari anticaptcha_key.txt.{Style.RESET_ALL}")
                return captcha_key
        except FileNotFoundError:
            self.log(f"{Fore.RED + Style.BRIGHT}File 'anticaptcha_key.txt' tidak ditemukan. Pastikan Anda memiliki kunci Anti-Captcha yang valid di dalamnya.{Style.RESET_ALL}")
            return None
        except Exception as e:
            self.log(f"{Fore.RED + Style.BRIGHT}Gagal memuat kunci Anti-Captcha: {e}{Style.RESET_ALL}")
            return None
    
    async def load_proxies(self, use_proxy_choice: bool):
        filename = "proxy.txt"
        try:
            if use_proxy_choice == 1:
                async with ClientSession(timeout=ClientTimeout(total=30)) as session:
                    async with session.get("https://api.proxyscrape.com/v4/free-proxy-list/get?request=display_proxies&proxy_format=protocolipport&format=text") as response:
                        response.raise_for_status()
                        content = await response.text()
                        with open(filename, 'w') as f:
                            f.write(content)
                        self.proxies = [line.strip() for line in content.splitlines() if line.strip()]
            else: # use_proxy_choice == 2 (private proxy)
                if not os.path.exists(filename):
                    self.log(f"{Fore.RED + Style.BRIGHT}File {filename} Tidak Ditemukan.{Style.RESET_ALL}")
                    return
                with open(filename, 'r') as f:
                    self.proxies = [line.strip() for line in f.read().splitlines() if line.strip()]
            
            if not self.proxies:
                self.log(f"{Fore.RED + Style.BRIGHT}Tidak Ada Proxy Yang Ditemukan.{Style.RESET_ALL}")
                return

            self.log(
                f"{Fore.GREEN + Style.BRIGHT}Total Proxy   : {Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT}{len(self.proxies)}{Style.RESET_ALL}"
            )
        
        except Exception as e:
            self.log(f"{Fore.RED + Style.BRIGHT}Gagal Memuat Proxy: {e}{Style.RESET_ALL}")
            self.proxies = []

    def check_proxy_schemes(self, proxies):
        schemes = ["http://", "https://", "socks4://", "socks5://"]
        if any(proxies.startswith(scheme) for scheme in schemes):
            return proxies
        return f"http://{proxies}" # Default ke http:// jika tidak ada skema

    def get_next_proxy_for_account(self, account):
        if account not in self.account_proxies:
            if not self.proxies:
                return None
            proxy = self.check_proxy_schemes(self.proxies[self.proxy_index])
            self.account_proxies[account] = proxy
            self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        return self.account_proxies[account]

    def rotate_proxy_for_account(self, account):
        if not self.proxies:
            return None
        proxy = self.check_proxy_schemes(self.proxies[self.proxy_index])
        self.account_proxies[account] = proxy
        self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        return proxy
    
    def generate_address(self, private_key: str):
        try:
            account = Account.from_key(private_key)
            address = account.address
            
            return address
        except Exception as e:
            return None
    
    def generate_payload(self, account: str, address: str, nonce: str):
        try:
            timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
            message = f"campaign.cicada.finance wants you to sign in with your Ethereum account:\n{address}\n\nBy signing, you are proving you own this wallet and logging in. This does not initiate a transaction or cost any fees.\n\nURI: https://campaign.cicada.finance\nVersion: 1\nChain ID: 56\nNonce: {nonce}\nIssued At: {timestamp}\nResources:\n- https://privy.io"
            encoded_message = encode_defunct(text=message)
            signed_message = Account.sign_message(encoded_message, private_key=account)
            signature = to_hex(signed_message.signature)

            payload = {
                "message":message,
                "signature":signature,
                "chainId":"eip155:56",
                "walletClientType":"okx_wallet",
                "connectorType":"injected",
                "mode":"login-or-sign-up"
            }

            return payload
        except Exception as e:
            raise Exception(f"Gagal Membuat Payload Permintaan: {str(e)}")
    
    def mask_account(self, account):
        try:
            mask_account = account[:6] + '*' * 6 + account[-6:]
            return mask_account
        except Exception as e:
            return None

    def print_question(self):
        while True:
            try:
                print(f"{Fore.WHITE + Style.BRIGHT}1. Jalankan Dengan Proxy Gratis Proxyscrape{Style.RESET_ALL}")
                print(f"{Fore.WHITE + Style.BRIGHT}2. Jalankan Dengan Proxy Pribadi{Style.RESET_ALL}")
                print(f"{Fore.WHITE + Style.BRIGHT}3. Jalankan Tanpa Proxy (Untuk Koneksi Utama Bot){Style.RESET_ALL}") # Menambahkan peringatan
                choose = int(input(f"{Fore.BLUE + Style.BRIGHT}Pilih [1/2/3] -> {Style.RESET_ALL}").strip())

                if choose in [1, 2, 3]:
                    proxy_type = (
                        "Dengan Proxy Gratis Proxyscrape" if choose == 1 else 
                        "Dengan Proxy Pribadi" if choose == 2 else 
                        "Tanpa"
                    )
                    print(f"{Fore.GREEN + Style.BRIGHT}Mode Proxy {proxy_type} Dipilih.{Style.RESET_ALL}")
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Masukkan angka 1, 2, atau 3.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Input tidak valid. Masukkan angka (1, 2 atau 3).{Style.RESET_ALL}")

        rotate = False
        if choose in [1, 2]:
            while True:
                rotate = input(f"{Fore.BLUE + Style.BRIGHT}Putar Proxy Tidak Valid? [y/n] -> {Style.RESET_ALL}").strip()

                if rotate in ["y", "n"]:
                    rotate = rotate == "y"
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Input tidak valid. Masukkan 'y' atau 'n'.{Style.RESET_ALL}")

        return choose, rotate
    
    async def solve_cf_turnstile(self, retries=5): # Parameter 'proxy' dihapus karena Proxyless
        for attempt in range(retries):
            try:
                if self.CAPTCHA_KEY is None:
                    self.log(f"{Fore.RED + Style.BRIGHT}Kunci API Anti-Captcha tidak dimuat. Tidak dapat memecahkan captcha.{Style.RESET_ALL}")
                    return None
                
                self.log(f"{Fore.YELLOW + Style.BRIGHT}Menggunakan Anti-Captcha Proxyless untuk memecahkan Turnstile...{Style.RESET_ALL}")

                # Inisialisasi solver TurnstileProxyless
                solver = turnstileProxyless()
                solver.set_verbose(1) # Atur ke 1 untuk melihat detail log dari pustaka Anti-Captcha
                solver.set_key(self.CAPTCHA_KEY)
                solver.set_website_url(self.PRIVY_API) # Situs tempat captcha muncul
                solver.set_website_key(self.SITE_KEY)
                # Anda bisa menambahkan action, cData, chlPageData jika diperlukan, tapi untuk kasus ini mungkin tidak.
                # solver.set_action("some action")
                # solver.set_cdata("cdata_token")
                # solver.set_chlpagedata("chlpagedata_token")

                # Atur softId jika Anda memilikinya dari Anti-Captcha Dev Center
                # solver.set_soft_id(0) # Ganti 0 dengan softId Anda

                token = solver.solve_and_return_solution()

                if token != 0:
                    self.log(f"{Fore.GREEN + Style.BRIGHT}Captcha Turnstile Berhasil Dipecahkan!{Style.RESET_ALL}")
                    return token
                else:
                    self.log(f"{Fore.RED + Style.BRIGHT}Anti-Captcha Gagal memecahkan Turnstile: {solver.error_code}{Style.RESET_ALL}")
                    # Jika ada kesalahan, coba lagi setelah jeda
                    await asyncio.sleep(5)
                    continue # Lanjut ke percobaan berikutnya
            except Exception as e:
                self.log(f"{Fore.RED + Style.BRIGHT}Kesalahan tak terduga saat memecahkan Turnstile: {e}{Style.RESET_ALL}")
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                return None
        return None # Mengembalikan None jika semua percobaan gagal
    
    async def check_connection(self, proxy=None):
        connector = ProxyConnector.from_url(proxy) if proxy else None
        try:
            async with ClientSession(connector=connector, timeout=ClientTimeout(total=30)) as session:
                async with session.post(url="http://ip-api.com/json") as response:
                    response.raise_for_status()
                    return await response.json()
        except (Exception, ClientResponseError) as e:
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}Status    :{Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT} Koneksi Tidak 200 OK {Style.RESET_ALL}"
                f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
            )
            return None
            
    async def init(self, address: str, turnstile_token: str, proxy=None, retries=5):
        url = f"{self.PRIVY_API}/api/v1/siwe/init"
        data = json.dumps({"address":address, "token":turnstile_token})
        headers = {
            **self.PRIVY_HEADERS[address],
            "Content-Length": str(len(data)),
            "Content-Type": "application/json"
        }
        await asyncio.sleep(3)
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.post(url=url, headers=headers, data=data, ssl=False) as response:
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(
                    f"{Fore.MAGENTA+Style.BRIGHT} ● {Style.RESET_ALL}"
                    f"{Fore.BLUE+Style.BRIGHT}Status  :{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} Gagal Mendapatkan Nonce {Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
                )

        return None
    
    async def authenticate(self, account: str, address: str, nonce: str, proxy=None, retries=5):
        url = f"{self.PRIVY_API}/api/v1/siwe/authenticate"
        data = json.dumps(self.generate_payload(account, address, nonce))
        headers = {
            **self.PRIVY_HEADERS[address],
            "Content-Length": str(len(data)),
            "Content-Type": "application/json"
        }
        await asyncio.sleep(3)
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.post(url=url, headers=headers, data=data, ssl=False) as response:
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(
                    f"{Fore.MAGENTA+Style.BRIGHT} ● {Style.RESET_ALL}"
                    f"{Fore.BLUE+Style.BRIGHT}Status  :{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} Login Gagal {Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
                )

        return None

    async def user_verify(self, address: str, proxy=None, retries=5):
        url = f"{self.BASE_API}/users/referrals/{self.REF_CODE}?campaignId=440"
        headers = {
            **self.BASE_HEADERS[address],
            "Content-Length": "0",
            "Cookie": self.header_cookies[address]
        }
        await asyncio.sleep(3)
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.post(url=url, headers=headers, ssl=False) as response:
                        if response.status in [400, 403]:
                            return None
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}Status    :{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} Verifikasi Gagal {Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
                )
            
        return None
    
    async def task_lists(self, address: str, proxy=None, retries=5):
        url = f"{self.BASE_API}/campaigns/440/tasks"
        headers = {
            **self.BASE_HEADERS[address],
            "Authorization": f"Bearer {self.access_tokens[address]}",
            "Cookie": self.header_cookies[address]
        }
        await asyncio.sleep(3)
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.get(url=url, headers=headers, ssl=False) as response:
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}Daftar Tugas:{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} Gagal Mendapatkan Daftar {Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
                )
            
        return None
    
    async def add_points(self, address: str, task_id: int, proxy=None, retries=5):
        url = f"{self.BASE_API}/points/add"
        data = json.dumps({"taskId":task_id})
        headers = {
            **self.BASE_HEADERS[address],
            "Authorization": f"Bearer {self.access_tokens[address]}",
            "Content-Length": str(len(data)),
            "Content-Type": "application/json",
            "Cookie": self.header_cookies[address]
        }
        await asyncio.sleep(3)
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.post(url=url, headers=headers, data=data, ssl=False) as response:
                        if response.status == 409:
                            self.log(
                                f"{Fore.CYAN+Style.BRIGHT}      > {Style.RESET_ALL}"
                                f"{Fore.BLUE+Style.BRIGHT}Status:{Style.RESET_ALL}"
                                f"{Fore.YELLOW+Style.BRIGHT} Sudah Selesai {Style.RESET_ALL}"
                            )
                            return None
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}      > {Style.RESET_ALL}"
                    f"{Fore.BLUE+Style.BRIGHT}Status:{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} Belum Selesai {Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
                )
            
        return None
    
    async def gems_credit(self, address: str, task_id: int, proxy=None, retries=5):
        url = f"{self.BASE_API}/gems/credit"
        data = json.dumps({"transactionType":"TASK", "options":{"taskId":task_id}})
        headers = {
            **self.BASE_HEADERS[address],
            "Authorization": f"Bearer {self.access_tokens[address]}",
            "Content-Length": str(len(data)),
            "Content-Type": "application/json",
            "Cookie": self.header_cookies[address]
        }
        await asyncio.sleep(3)
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.post(url=url, headers=headers, data=data, ssl=False) as response:
                        if response.status == 409:
                            self.log(
                                f"{Fore.CYAN+Style.BRIGHT}      > {Style.RESET_ALL}"
                                f"{Fore.BLUE+Style.BRIGHT}Permata  :{Style.RESET_ALL}"
                                f"{Fore.YELLOW+Style.BRIGHT} Tidak Ada Hadiah {Style.RESET_ALL}"
                            )
                            return None
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}      > {Style.RESET_ALL}"
                    f"{Fore.BLUE+Style.BRIGHT}Permata  :{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} Tidak Ada Hadiah {Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
                )
            
        return None

    async def process_check_connection(self, address: str, use_proxy: bool, rotate_proxy: bool):
        while True:
            proxy = self.get_next_proxy_for_account(address) if use_proxy else None
            self.log(
                f"{Fore.CYAN + Style.BRIGHT}Proxy     :{Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT} {proxy if proxy else 'Tidak Ada Proxy'} {Style.RESET_ALL}"
            )

            check = await self.check_connection(proxy)
            if check and check.get("status") == "success":
                return True

            if rotate_proxy:
                proxy = self.rotate_proxy_for_account(address)
                await asyncio.sleep(5)
                continue
            
            self.log(f"{Fore.RED + Style.BRIGHT}Gagal terhubung ke internet. Memulai ulang percobaan koneksi.{Style.RESET_ALL}")
            await asyncio.sleep(10)
        
    async def process_get_nonce(self, address: str, use_proxy: bool, rotate_proxy: bool):
        is_valid = await self.process_check_connection(address, use_proxy, rotate_proxy)
        if is_valid:
            # Pustaka anticaptchaofficial.turnstileproxyless tidak memerlukan proxy di parameter solve_cf_turnstile
            turnstile_token = await self.solve_cf_turnstile() 
            if turnstile_token:
                self.log(
                    f"{Fore.MAGENTA+Style.BRIGHT} ● {Style.RESET_ALL}"
                    f"{Fore.BLUE+Style.BRIGHT}Pesan :{Style.RESET_ALL}"
                    f"{Fore.GREEN+Style.BRIGHT} Captcha Turnstile Berhasil Dipecahkan {Style.RESET_ALL}"
                )

                # Untuk init, authenticate, dll., kita masih menggunakan proxy yang dipilih user
                proxy_for_main_requests = self.get_next_proxy_for_account(address) if use_proxy else None
                init = await self.init(address, turnstile_token, proxy_for_main_requests)
                if init:
                    nonce = init["nonce"]
                    return nonce

                return False
            
            self.log(
                f"{Fore.MAGENTA+Style.BRIGHT} ● {Style.RESET_ALL}"
                f"{Fore.BLUE+Style.BRIGHT}Pesan :{Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT} Captcha Turnstile Gagal Dipecahkan {Style.RESET_ALL}"
            )
            return False

    async def process_user_login(self, account: str, address: str, use_proxy: bool, rotate_proxy: bool):
        nonce = await self.process_get_nonce(address, use_proxy, rotate_proxy)
        if nonce:
            proxy = self.get_next_proxy_for_account(address) if use_proxy else None

            login = await self.authenticate(account, address, nonce, proxy)
            if login:
                self.privy_id[address] = login["user"]["id"]
                self.access_tokens[address] = login["token"]
                self.identity_tokens[address] = login["identity_token"]
                self.header_cookies[address] = f"privy-token={self.access_tokens[address]}; privy-id-token={self.identity_tokens[address]}"

                self.log(
                    f"{Fore.MAGENTA+Style.BRIGHT} ● {Style.RESET_ALL}"
                    f"{Fore.BLUE+Style.BRIGHT}Status  :{Style.RESET_ALL}"
                    f"{Fore.GREEN+Style.BRIGHT} Login Berhasil {Style.RESET_ALL}"
                )
                return True

            return False
            
    async def process_accounts(self, account: str, address: str, use_proxy: bool, rotate_proxy: bool):
        logined = await self.process_user_login(account, address, use_proxy, rotate_proxy)
        if logined:
            proxy = self.get_next_proxy_for_account(address) if use_proxy else None

            await self.user_verify(address, proxy)

            task_lists = await self.task_lists(address, proxy)
            if task_lists:
                self.log(f"{Fore.CYAN+Style.BRIGHT}Daftar Tugas:{Style.RESET_ALL}")

                all_tasks = [task for task in task_lists if task]

                for task in task_lists:
                    sub_tasks = task.get("subtasks", [])
                    all_tasks.extend([sub_task for sub_task in sub_tasks if sub_task])

                for task in all_tasks:
                    task_id = task.get("id")
                    title = task.get("title")
                    reward = task.get("points")

                    self.log(
                        f"{Fore.MAGENTA+Style.BRIGHT}   ● {Style.RESET_ALL}"
                        f"{Fore.WHITE+Style.BRIGHT}{title}{Style.RESET_ALL}"
                    )

                    added = await self.add_points(address, task_id, proxy)
                    if added:
                        self.log(
                            f"{Fore.CYAN+Style.BRIGHT}      > {Style.RESET_ALL}"
                            f"{Fore.BLUE+Style.BRIGHT}Status:{Style.RESET_ALL}"
                            f"{Fore.GREEN+Style.BRIGHT} Selesai {Style.RESET_ALL}"
                        )
                        self.log(
                            f"{Fore.CYAN+Style.BRIGHT}      > {Style.RESET_ALL}"
                            f"{Fore.BLUE+Style.BRIGHT}Poin :{Style.RESET_ALL}"
                            f"{Fore.WHITE+Style.BRIGHT} {reward} {Style.RESET_ALL}"
                        )

                    gems = await self.gems_credit(address, task_id, proxy)
                    if gems:
                        credit = gems.get("credit", 0)

                        self.log(
                            f"{Fore.CYAN+Style.BRIGHT}      > {Style.RESET_ALL}"
                            f"{Fore.BLUE+Style.BRIGHT}Permata  :{Style.RESET_ALL}"
                            f"{Fore.WHITE+Style.BRIGHT} {credit} {Style.RESET_ALL}"
                        )

    async def main(self):
        try:
            with open('accounts.txt', 'r') as file:
                accounts = [line.strip() for line in file if line.strip()]

            anticaptcha_key = self.load_anticaptcha_key()
            if anticaptcha_key:
                self.CAPTCHA_KEY = anticaptcha_key
            else:
                self.log(f"{Fore.RED + Style.BRIGHT}Kunci Anti-Captcha tidak ditemukan. Bot akan keluar.{Style.RESET_ALL}")
                return 

            use_proxy_choice, rotate_proxy = self.print_question()

            use_proxy = False
            if use_proxy_choice in [1, 2]:
                use_proxy = True

            while True:
                self.clear_terminal()
                self.welcome()
                self.log(
                    f"{Fore.GREEN + Style.BRIGHT}Total Akun: {Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT}{len(accounts)}{Style.RESET_ALL}"
                )

                if use_proxy:
                    await self.load_proxies(use_proxy_choice)
                else:
                    self.log(f"{Fore.YELLOW + Style.BRIGHT}Peringatan: Anda memilih 'Tanpa Proxy' untuk koneksi utama bot. Pastikan koneksi Anda stabil.{Style.RESET_ALL}")

                separator = "=" * 25
                for account in accounts:
                    if account:
                        address = self.generate_address(account)
                        self.log(
                            f"{Fore.CYAN + Style.BRIGHT}{separator}[{Style.RESET_ALL}"
                            f"{Fore.WHITE + Style.BRIGHT} {self.mask_account(address)} {Style.RESET_ALL}"
                            f"{Fore.CYAN + Style.BRIGHT}]{separator}{Style.RESET_ALL}"
                        )

                        if not address:
                            self.log(
                                f"{Fore.CYAN+Style.BRIGHT}Status    :{Style.RESET_ALL}"
                                f"{Fore.RED + Style.BRIGHT} Private Key Tidak Valid atau Versi Library Tidak Didukung {Style.RESET_ALL}"
                            )
                            continue

                        user_agent = random.choice(USER_AGENT)

                        self.PRIVY_HEADERS[address] = {
                            "Accept": "application/json",
                            "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
                            "Origin": "https://campaign.cicada.finance",
                            "Privy-App-Id": "cltgsatvl0uwg126o8osk48a3",
                            "Privy-Client-Id": "client-WY2ifxw6VQBxyc2wm9qFMambiP3khbmE57s6Dov2WVpDA",
                            "Referer": "https://campaign.cicada.finance/", 
                            "Sec-Fetch-Dest": "empty",
                            "Sec-Fetch-Mode": "cors",
                            "Sec-Fetch-Site": "cross-site",
                            "Sec-Fetch-Storage-Access": "active",
                            "User-Agent": user_agent
                        }

                        self.BASE_HEADERS[address] = {
                            "Accept": "*/*",
                            "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
                            "Origin": "https://campaign.cicada.finance",
                            "Referer": "https://campaign.cicada.finance/", 
                            "Sec-Fetch-Dest": "empty",
                            "Sec-Fetch-Mode": "cors",
                            "Sec-Fetch-Site": "same-origin",
                            "User-Agent": user_agent
                        }

                        await self.process_accounts(account, address, use_proxy, rotate_proxy)
                        await asyncio.sleep(3)

                self.log(f"{Fore.CYAN + Style.BRIGHT}={Style.RESET_ALL}"*72)
                
                delay = 24 * 60 * 60
                while delay > 0:
                    formatted_time = self.format_seconds(delay)
                    print(
                        f"{Fore.CYAN+Style.BRIGHT}[ Tunggu selama{Style.RESET_ALL}"
                        f"{Fore.WHITE+Style.BRIGHT} {formatted_time} {Style.RESET_ALL}"
                        f"{Fore.CYAN+Style.BRIGHT}... ]{Style.RESET_ALL}"
                        f"{Fore.WHITE+Style.BRIGHT} | {Style.RESET_ALL}"
                        f"{Fore.YELLOW+Style.BRIGHT}Semua Akun Telah Diproses...{Style.RESET_ALL}",
                        end="\r",
                        flush=True
                    )
                    await asyncio.sleep(1)
                    delay -= 1

        except FileNotFoundError:
            self.log(f"{Fore.RED}File 'accounts.txt' Tidak Ditemukan.{Style.RESET_ALL}")
            return
        except Exception as e:
            self.log(f"{Fore.RED+Style.BRIGHT}Error: {e}{Style.RESET_ALL}")
            raise e

if __name__ == "__main__":
    try:
        bot = Cicada()
        asyncio.run(bot.main())
    except KeyboardInterrupt:
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
            f"{Fore.RED + Style.BRIGHT}[ KELUAR ] Cicada - BOT{Style.RESET_ALL}                                      "      
        )
