from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

from utils.checks import FileCheck
from cookies import Cookies

import json
import sys
import os
import time
import random

opts = Options()


def load_settings():
    fchk = FileCheck()
    fchk.check_create_folder("data")
    fchk.check_copy_file("data/settings.json")
    with open("data/settings.json") as f:
        print("[INFO] Loaded settings.")
        return json.load(f)


def parse_arguments():      
    """
    ################### Read ######################
    
        -h stands for headless mode
        -hot stands for checking the posts in hot

    """
    global opts
    opts.start = 9

    for arg in sys.argv:
        if arg == "-h":
            opts.add_argument("--headless")
        elif arg == "-hot":
            opts.start = 0


class InstagramBot:
    # todo: clear follow list
    def __init__(self, username=None, password=None):

        parse_arguments()
    
        if os.name == "posix":
            exec_path = "./chromedriver"
        else:
            exec_path = "chromedriver.exe"

        self.settings = load_settings()
        self.username, self.password = self.process_credentials(username, password)
        self.comm_counter = 0
        self.browser = webdriver.Chrome(options=opts, executable_path=exec_path)
        self.cookies = Cookies(self.browser)

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

        # saving login details
        save_login_btn = self.browser.find_element_by_css_selector("button")
        save_login_btn.click()
        self.cookies.save()

    def exit(self):
        """Exit the bot process"""
        time.sleep(5)
        self.browser.quit()

    def inject_cookies(self):
        """Insert previous existing cookies"""
        self.cookies.load()
        prev_cookies = self.cookies.get()
        if not prev_cookies:
            self.sign_in()
        else:
            try:
                self.cookies.inject()
            except Cookies.TooOldException:
                self.sign_in()

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

    @staticmethod
    def like(buttons):
        """Like a post"""
        time.sleep(2)

        like_btn = buttons[2]
        # h, w = like_btn.size["height"], like_btn.size["width"]
        h, w = like_btn.size.values()
        if not h == w == 40:
            like_btn = buttons[3]
        like_btn.click()

    @staticmethod
    def follow(buttons):
        """Folow a post's author"""
        follow_btn = buttons[0]
        if follow_btn.text.lower() == "follow":
            follow_btn.click()
            time.sleep(2)

    def comment(self):
        """Comment on a post"""
        comm_box = self.browser.find_elements_by_css_selector("form textarea")
        if not comm_box:
            return

        comm_box = comm_box[0]
        comm_box.click()
        comm_box = self.browser.find_element_by_css_selector("form textarea")

        # todo: send random number of comments
        comm_choice = random.choice(self.settings["base_comments"])
        comm_box.send_keys(comm_choice)

        post_button = self.browser.find_element_by_css_selector("form button")
        post_button.click()

        self.comm_counter += 1
        if self.comm_counter == 5:
            self.comm_counter = 0
            print("Waiting 5 seconds to avoid soft ban")
            time.sleep(10)

        time.sleep(2)

    def process_posts(self, links):
        for i in range(opts.start, len(links)):
            post_url = links[i]
            # todo: check if post was previously seen
            print(post_url)

            self.browser.get(post_url)
            buttons = self.browser.find_elements_by_css_selector("button")
            self.follow(buttons)
            self.like(buttons)
            self.comment()

    def get_following(self):
        """Retrieves links to the users the bot is following"""
        self.browser.get(f"https://www.instagram.com/{self.username}/")
        time.sleep(1)

        following_btn = self.browser.find_elements_by_css_selector("ul li a")[1]
        following_btn.click()
        time.sleep(1)

        following_window = self.browser.find_element_by_css_selector('div[role=\'dialog\'] ul')
        following_window.click()
        time.sleep(2)

        # todo: scroll till the end of the page
        height = following_window.size["height"]
        action_chain = webdriver.ActionChains(self.browser)
        while True:
            action_chain.send_keys(Keys.SPACE).perform()
            time.sleep(5)

            following_window = self.browser.find_element_by_css_selector('div[role=\'dialog\'] ul')
            following_window.click()

            new_height = following_window.size["height"]
            if new_height == height:
                break
            height = new_height

        following_list = following_window.find_elements_by_css_selector("li")
        following_links = list()
        for user in following_list:
            link = user.find_element_by_css_selector('a').get_attribute('href')
            following_links.append(link)
        return following_links

    def unfollow(self, user_link):
        self.browser.get(user_link)
        time.sleep(2)

        unfollow_btn_path = "/html/body/div[1]/section/main/div/header/section/div[1]/div[2]/div/span/span[1]/button"
        unfollow_btn = self.browser.find_elements_by_xpath(unfollow_btn_path)
        if not unfollow_btn:
            return
        unfollow_btn[0].click()
        time.sleep(1)

        confirm_btn_path = "/html/body/div[4]/div/div/div/div[3]/button[1]"
        confirm_btn = self.browser.find_element_by_xpath(confirm_btn_path)
        confirm_btn.click()

    def unfollow_many(self, count=1):
        following_links = self.get_following()
        following_links = enumerate(reversed(following_links))
        for index, user_link in following_links:
            self.unfollow(user_link)
            if index == count - 1:
                break
