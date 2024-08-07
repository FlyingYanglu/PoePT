from poept import PoePT
import threading
import time
#setup needed everytime
bot = PoePT()
bot.login("yang_huibo@outlook.com")

with open("D:/Downloads/tool/PoePT/poept/examples/prompt.txt", "r", encoding="utf-8") as f:
    prompt = f.read()

print("Prompt:", prompt)

#asking prompt in a loop
while (True):
    response = bot.ask(newchat=False, bot="Claude-3-Haiku", prompt=prompt)
    print(response)
    time.sleep(5)
    if(prompt=="exit"): break

# #asking prompt with attached file
# import os
# prompt = input("> ")
# file = os.path.abspath("test.jpg")
# response = bot.ask(bot="Assistant", prompt=prompt, attach_file=file)
# print(response)
