"""
PoePT Python Library.
#########################################

Usage --> ``bot = PoePT()``

Example -->

```
from poept import PoePT

bot = PoePT(headless=True)
bot.login("<your_email>")

while (True):
    prompt = input("> ")
    response = bot.ask(bot="Assistant", prompt=prompt)
    print(response)
    if(prompt=="exit"): break

bot.close()
```

# (The PoePT object needs to call login method)

#########################################
"""

import os
import json
import logging
from seleniumbase import Driver, SB
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from poept.exceptions import ToomanyRequestsException, TimeoutException, TooLongResponseException
from selenium.webdriver.support import expected_conditions as EC
from .tools import speech, record
from selenium.webdriver.common.keys import Keys
import json
import time


# Configure logging
logging.basicConfig(filename='poebot.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class PoePT:
    def __init__(self, 
                 headless=True, #Whether to run the browser in headless mode
        ):
        """
        Initialize the PoePT class with optional headless browser mode.
        """
        if not isinstance(headless, bool):
            raise ValueError("headless must be a boolean value.")
        
        self.headless = headless
        options = {
            "headless": headless,
            "headless1": headless,
            "headless2": headless,
        }
        self.driver = Driver(**options)
        self.status = "false"
        self.current_bot = ""
        self.prompt = ""
        self.response = ""
        self.config()

    def clear_cookies(self):
        """
        Clear all cookies from the current driver session.
        
        Returns:
        - bool: True if cookies were cleared successfully, False otherwise.
        """
        if self.driver:
            self.driver.delete_all_cookies()
            print("Cookies cleared.")
            return True
        return False

    def load_cookies(self):
        """
        Load cookies from a saved file and add them to the current driver session.
        
        Returns:
        - bool: True if cookies were loaded successfully, False otherwise.
        """
        if self.driver:
            with open(f"saved_cookies/cookies_{self.email}.txt", 'r') as f:
                cookies = json.load(f)
            for cookie in cookies:
                self.driver.add_cookie(cookie)
            return True
        return False

    def config(self, website="https://poe.com/", #Base URL of POE.
               email_form=".textInput_input__9YpqY", #CSS selector for the email input form.
               go_btn=".Button_buttonBase__Bv9Vx.Button_primary__6UIn0",  #CSS selector for the 'Go' button.
               code_form=".VerificationCodeInput_verificationCodeInput__RgX85", #CSS selector for the verification code input div.
               login_btn=".Button_buttonBase__Bv9Vx.Button_primary__6UIn0",  #CSS selector for the login button.
               query_input_form=".GrowingTextArea_textArea__ZWQbP", #CSS selector for the chat input div.
               query_send_btn=".ChatMessageSendButton_sendButton__4ZyI4",  #CSS selector for the chat send button.
               clear_key_btn=".ChatBreakButton_button__zyEye", #CSS selector for the clear chat button.
               file_input_form=".ChatMessageFileInputButton_input__svNx4",  #CSS selector for the file input div.
               file_input_box=".ChatMessageInputAttachments_container__AAxGu", #CSS selector for the file input box in chat.
               voice_input_btn=".ChatMessageVoiceInputButton_button__NjXno",  #CSS selector for the voice input button.
               msg_element=".ChatMessage_chatMessage__xkgHx", #CSS selector for the response message element div.
               msg_image="MarkdownImage_image__3dBzJ",#CSS selector for the response message picture element img.
               msg_pair=".ChatMessagesView_messagePair__ZEXUz"
            ):
        """
        Configure the web elements' selectors for interaction.
        """
        self.website = website
        self.clear_key_btn = clear_key_btn
        self.email_form = email_form
        self.go_btn = go_btn
        self.code_form = code_form
        self.login_btn = login_btn
        self.query_input_form = query_input_form
        self.query_send_btn = query_send_btn
        self.file_input_form = file_input_form
        self.file_input_box = file_input_box
        self.voice_input_btn = voice_input_btn
        self.msg_element = msg_element
        self.msg_image = msg_image
        self.msg_pair = msg_pair

    def login(self, 
              email #Email address used for login.
              ):
        """
        Log in to the website using the provided email. 
        If cookies are saved, load them instead.

        Returns:
        - bool: True if login successful, False otherwise.
        """
        self.email = email
        if not isinstance(email, str):
            raise ValueError("email must be a string.")
        
        if os.path.exists(f"saved_cookies/cookies_{email}.txt"):
            logging.info(f"Existing cookies found at ./saved_cookies/cookies_{email}.txt")
            self.status = "ready"
            return True

        try:
            with SB(headless2=self.headless) as sb:
                sb.open(self.website)
                sb.type(self.email_form, email)
                sb.click(self.go_btn)
                print("Verification email sent...")
                sb.assert_element(self.code_form)

                code = input("Enter Code: ")
                sb.type(self.code_form, code)
                sb.click(self.login_btn)
                sb.assert_element(self.query_input_form)
                sb.save_cookies(name=f"cookies_{email}.txt")
                self.status = "ready"
                return True
            
        except Exception as e:
            logging.error("Login Error: WebDriver not initialized.")
            logging.error(e)
            return False

    def ask(self, 
            newchat=True, #Flag indicating whether to start a new chat session. ignored if its first question
            bot="Assistant", #Username of the bot to interact with.
            prompt="", #Query message to send to the bot.
            attach_file="", #Absolute path of a file to attach (if any).
            img_output=False, #If the response should contain an image.
            ):
        """
        Send a query to the chatbot and receive a response.
        
        Returns:
        - str: Response from the chatbot.
        """
        if not isinstance(newchat, bool):
            raise ValueError("newchat must be a boolean value.")
        if not isinstance(bot, str):
            raise ValueError("bot must be a string.")
        if not isinstance(prompt, str):
            raise ValueError("prompt must be a string.")
        if not isinstance(attach_file, str):
            raise ValueError("attach_file must be a string.")
        
        if not self.driver:
            logging.error("WebDriver not initialized. Please login first.")
            raise RuntimeError("WebDriver not initialized. Please login first.")

        self.status = "wait"

        if newchat or self.current_bot != bot:
            self.driver.get(f"{self.website}{bot}")
            self.current_bot = bot
            self.load_cookies()
            self.driver.refresh()
            try:
                WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, self.query_input_form)))
            except Exception as e:
                raise TimeoutException("Timeout after 10 seconds.")
        
        try:
            self.prompt = prompt
            # self.driver.find_element(By.CSS_SELECTOR, self.query_input_form).send_keys(prompt)
            input_form = self.driver.find_element(By.CSS_SELECTOR, self.query_input_form)
            # input_form.clear()
            # for line in prompt.split('\n'):
            #     input_form.send_keys(line)
            #     input_form.send_keys(Keys.SHIFT, Keys.ENTER)
            escaped_prompt = prompt.replace('`', '\\`')
            self.driver.execute_script(f"""arguments[0].value = `{escaped_prompt}`;""", input_form)
            input_form.send_keys(Keys.SPACE)

            if attach_file:
                if not os.path.exists(attach_file):
                    raise FileNotFoundError(f"The file {attach_file} does not exist.")
                self.driver.find_element(By.CSS_SELECTOR, self.file_input_form).send_keys(attach_file)
                WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, self.file_input_box)))

            num_msgs = len(self.driver.find_elements(By.XPATH, f"//div[@class='{self.msg_pair[1:]}']"))
            self.driver.find_element(By.CSS_SELECTOR, self.query_send_btn).click()
            try:
                WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, self.msg_element)))
            except Exception as e:
                raise TimeoutException("Timeout after 10 seconds.")
            start_time = time.time()
            num_continuous_increase = 10
            while True:
                num_msgs_new = len(self.driver.find_elements(By.XPATH, f"//div[@class='{self.msg_pair[1:]}']"))
                if num_msgs_new == num_msgs + 1:
                    num_continuous_increase -= 1
                else:
                    num_continuous_increase = 10
                if num_continuous_increase == 0:
                    break
                time.sleep(0.25)
                # if current time - start time > 15mins, raise exception
                if time.time() - start_time > 900:
                    raise TimeoutException("Timeout after 15 minutes.")
            

            new_msg_pair = self.driver.find_element(By.XPATH, f"//div[@class='{self.msg_pair[1:]}'][last()]")
        
            while True:
                msgs = new_msg_pair.find_elements(By.XPATH, f".//div[@class='{self.msg_element[1:]}']")
                if len(msgs) >= 2:
                    if msgs[1].get_attribute("data-complete") == "true": 
                        self.response = msgs[1].text
                        break
                if time.time() - start_time > 900:
                    raise TimeoutException("Timeout after 15 minutes.")
            if "You are sending and" in self.response:
                raise ToomanyRequestsException("Rate limit exceeded. Please wait before sending another message.")
            if "This response was limited" in self.response:
                raise TooLongResponseException("Response too long. Please try again with a shorter prompt.")

            if "needs more points to answer your request" in self.response:
                raise TimeoutException("Rate limit exceeded. Please wait before sending another message.")
            self.response = '\n'.join(self.response.split('\n')[2:])
            if img_output:
                self.response += msg.find_element(By.CSS_SELECTOR, self.msg_image).get_attribute("src")

            self.status = "ready"
            return self.response
        
        except Exception as e:
            logging.error(f"Exception occurred in ask method: {e}")
            raise e
            return ""

    def clear_chat(self):
        """
        Clear the current chat session.
        
        Returns:
        - bool: True if chat cleared successfully, False otherwise.
        """
        if not self.driver:
            raise RuntimeError("WebDriver not initialized. Please login first.")
        try:
            self.driver.find_element(By.CSS_SELECTOR, self.clear_key_btn).click()
            print("Chat cleared.")
            return True
        
        except Exception as e:
            logging.error(e)
            return


    def file_voice(self, 
                   file="audio.wav", #Absolute path to the audio file.
                   ):
        """
        Convert a recorded audio file to text.
        
        Returns:
        - str: Text transcription of the audio file.
        """
        if not isinstance(file, str):
            raise ValueError("file must be a string.")
        if not os.path.exists(file):
            raise FileNotFoundError(f"The file {file} does not exist.")
        
        try:
            prompt = speech(file)
            return prompt
        except Exception as e:
            logging.error(e)
            return
    
    def close(self):
        """
        Close the browser session.
        """
        if self.driver:
            self.driver.quit()
