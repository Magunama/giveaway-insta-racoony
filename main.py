import os
import time
import random
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from utils.checks import FileCheck
import json
import sys


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

# todo: clear follow list


class InstagramBot:
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

    @staticmethod
    def like(buttons):
        time.sleep(2)

        like_btn = buttons[2]
        # h, w = like_btn.size["height"], like_btn.size["width"]
        h, w = like_btn.size.values()
        if not h == w == 40:
            like_btn = buttons[3]
        like_btn.click()

    @staticmethod
    def follow(buttons):
        follow_btn = buttons[0]
        if follow_btn.text.lower() == "follow":
            follow_btn.click()
            time.sleep(2)

    def comment(self):
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

    def get_following_list(self, username, num_of_users_to_delete):
        #todo: make something to scroll when opening followers list so you can get more
        time.sleep(2)
        self.browser.get("https://www.instagram.com/" + username + '/')

        following = self.browser.find_elements_by_css_selector("ul li a") [1]
        following.click()
        time.sleep(2)

        followers_list = self.browser.find_element_by_css_selector('div[role=\'dialog\'] ul')
        following_num = len(followers_list.find_elements_by_css_selector('li'))
        print(following_num)
        followers_list.click()

        following_list = []
        for user in followers_list.find_elements_by_css_selector('li'):
            link = user.find_element_by_css_selector('a').get_attribute('href')
            print(link)
            following_list.append(link)

        return following_list

    def unfollow_list(self, username, num):

        global unfollowButton
        links = self.get_following_list(username, num)

        for user in links:
            self.browser.get(user)
            time.sleep(2)

            buttons = self.browser.find_elements_by_css_selector('button')

            for button in buttons:
                if (button.text == "Following"):
                    unfollowButton = button

            if (unfollowButton.text == 'Following'):
                unfollowButton.click()
                time.sleep(2)
                confirmButton = self.browser.find_element_by_xpath('//button[text() = "Unfollow"]')
                confirmButton.click()
            else:
                print("Oops")