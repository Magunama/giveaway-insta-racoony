from main import InstagramBot

bot = InstagramBot()

# inserting previous existent cookies
bot.inject_cookies()

links = bot.search_giveaway()
bot.process_posts(links)

# bot.unfollow_many()

bot.exit()
