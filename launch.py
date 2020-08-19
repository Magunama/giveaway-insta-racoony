from main import InstagramBot

bot = InstagramBot()

bot.sign_in()
#links = bot.search_giveaway()
#bot.process_posts(links)
bot.unfollow_list("insta.racoony", 50)

bot.exit()
