import interactions

"""  
  _____       _     _ ___  ______                 
 |  __ \     (_)   | |__ \|  ____|                
 | |__) |__ _ _  __| |  ) | |__   __ _ _ __ _ __  
 |  _  // _` | |/ _` | / /|  __| / _` | '__| '_ \ 
 | | \ \ (_| | | (_| |/ /_| |___| (_| | |  | | | |
 |_|  \_\__,_|_|\__,_|____|______\__,_|_|  |_| |_|
                                                  
"""

bot = interactions.Client(token=open("token.txt", "r").read())

initial_ext = [
  	"cogs.events",
 	"cogs.user",
  	"cogs.admin",
	"cogs.create"
]

for extension in initial_ext:
  	bot.load(extension)
bot.start()