import os
import time
import random
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from utils.checks import FileCheck
import json


def load_settings():
    fchk = FileCheck()
    fchk.check_create_folder("data")
    fchk.check_copy_file("data/settings.json")
    with open("data/settings.json") as f:
        print("[INFO] Loaded settings.")
        return json.load(f)


class InstagramBot:
    def __init__(self, username=None, password=None):
        self.settings = load_settings()

        self.username, self.password = self.process_credentials(username, password)

        opts = Options()
        # opts.add_argument("--headless")
        if os.name == "posix":
            exec_path = "./chromedriver"
        else:
            exec_path = "chromedriver.exe"

        self.browser = webdriver.Chrome(options=opts, executable_path=exec_path)

    def process_credentials(self, username, password):
        if not username:
            username = self.settings["username"]
            if not username:
                username = input("Username: ")
        if not password:
            password = self.settings["password"]
            if not password:
                password = input("Password: ")
        return username, password

    def sign_in(self):
        """Sign in to Instagram with the provided credentials"""
        self.browser.get('https://www.instagram.com/accounts/login/')
        time.sleep(2)

        form = self.browser.find_elements_by_css_selector("form input")
        email_input = form[0]
        pass_input = form[1]

        email_input.send_keys(self.username)
        pass_input.send_keys(self.password)
        pass_input.send_keys(Keys.ENTER)
        time.sleep(2)

    def exit(self):
        """Exit the bot process"""
        self.browser.quit()

    def search_giveaway(self):
        """Retrieve a list of links of the latest posts tagged #giveaway"""
        self.browser.get('https://www.instagram.com/explore/tags/giveaway/')
        time.sleep(2)

        posts = self.browser.find_elements_by_css_selector("a[href^='/p/']")

        links = list()
        for post in posts:
            link = post.get_attribute("href")
            links.append(link)

        return links

    def show_source(self):
        """Show page source of current tab"""
        page_source = self.browser.page_source
        with open("page_source.html", "w", encoding="utf-8") as fp:
            fp.write(page_source)
        page_source_path = os.path.abspath("page_source.html")
        self.browser.execute_script(f"window.open('','_blank');")
        new_tab = self.browser.window_handles[1]
        self.browser.switch_to.window(new_tab)
        self.browser.get(f"file://{page_source_path}")
        old_tab = self.browser.window_handles[0]
        self.browser.switch_to.window(old_tab)

    def get_post_details(self, url):
        self.browser.get(url)

        buttons = self.browser.find_elements_by_css_selector("button")
        follow_btn = buttons[0]
        like_btn = buttons[2]
        # h, w = like_btn.size["height"], like_btn.size["width"]
        h, w = like_btn.size.values()
        if not h == w == 40:
            like_btn = buttons[3]

        comm_box = self.browser.find_elements_by_css_selector("form textarea")
        if comm_box:
            comm_box = comm_box[0]

        return [follow_btn, like_btn, comm_box]

    def process_posts(self, links):
        for i in range(9, len(links)):
            post_url = links[i]
            # todo: check if post was previously seen
            print(post_url)
            follow_btn, like_btn, comm_box = self.get_post_details(post_url)

            if follow_btn.text.lower() == "follow":
                follow_btn.click()
                time.sleep(2)

            like_btn.click()
            time.sleep(2)

            if not comm_box:
                time.sleep(2)
                return
            comm_box.click()
            comm_box = self.browser.find_element_by_css_selector("form textarea")
            comms = random.choice(self.settings["base_comments"])
            # todo: send random number of comments
            comm_box.send_keys(comms)
            comm_box.send_keys(Keys.ENTER)
            time.sleep(2)
