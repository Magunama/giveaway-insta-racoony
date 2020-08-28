from utils.checks import FileCheck

import json
import time


class Cookies:
    def __init__(self, browser):
        self.browser = browser
        self.path = "data/cookies.json"
        self.internal = []

    def get(self):
        return self.internal

    def save(self):
        new_cookies = self.browser.get_cookies()
        self.internal = new_cookies
        with open(self.path, "w") as fp:
            json.dump(new_cookies, fp, indent=4)
        print("[INFO] Saved cookies.")

    def load(self):
        FileCheck().check_create_file(self.path, "[]")
        with open(self.path) as fp:
            prev_cookies = json.load(fp)
        if prev_cookies:
            self.internal = prev_cookies
            print("[INFO] Loaded cookies.")
        else:
            print("[INFO] Cookie list is empty.")

    def clear(self):
        self.browser.delete_all_cookies()

    def inject(self):
        self.browser.get("https://www.instagram.com")
        for c in self.internal:
            if "expiry" in c:
                expiry = c["expiry"]
                now = int(time.time())
                if expiry - now < 0:
                    print("[INFO] Cookies are too old!\nUsing login and saving new cookies.")
                    raise self.TooOldException()
            self.browser.add_cookie(c)
        print("[INFO] Injected cookies.")

    class TooOldException(Exception):
        pass
