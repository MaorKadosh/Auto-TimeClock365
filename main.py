import os
import logging
from time import sleep
from sys import platform
from time import strftime
from dotenv import load_dotenv
from selenium import webdriver
from telegram.ext import ExtBot 
from telegram import TelegramError
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.support import expected_conditions as EC

# Loads constants
load_dotenv(".env")
BASE_URL = os.getenv("BASE_URL")
TIMECARD_URL = os.getenv("TIMECARD_URL")
USERNAME = os.getenv("TIME_CLOCK365_USERNAME")
PASSWORD = os.getenv("TIME_CLOCK365_PASSWORD")
os.environ["GH_TOKEN"] = os.getenv("GH_TOKEN")
SHIFT_START_TIME = strftime("%d.%m.20%y, ") + os.getenv("SHIFT_START_TIME")
SHIFT_END_TIME = strftime("%d.%m.20%y, ") + os.getenv("SHIFT_END_TIME")
HEADLESS = True if os.getenv("HEADLESS") == 'True' else False
OPERATIONAL = True if os.getenv("OPERATIONAL") == 'True' else False
TELEGRAM_TOKETN = os.getenv("TELEGRAM_TOKEN")   
TELEGRAM_ID = int(os.getenv("TELEGRAM_USER_ID"))


def reporter(message: str, image_path: str=None) -> None:
    logging.info(f"Start reporting using telegram")
    try:
        reporter = ExtBot(TELEGRAM_TOKETN)
        reporter.send_message(chat_id=TELEGRAM_ID, text=message)
        if image_path:
            with open(image_path, 'rb') as image:
                reporter.send_photo(chat_id=TELEGRAM_ID, photo=image)
    except TelegramError as e:
        logging.critical(f"Reporter caught an expetion unable to send messages to users: \n{e}\nend of Telegram exception")
   
    logging.info(f"Finish reporting")

def init() -> webdriver.Firefox:
    """
        Init a Selenium base on the OS and loads a web page using .env BASE_URL argument.

        :return webdriver: initiated webdriver with Firefox page loaded with BASE_URL page.
        :rtype: webdriver
    """
    logging.info("Initializing Browser")
    try:
        opt = Options()
        opt.headless = HEADLESS

        # Check running OS in order to start session correctly.
        if "win32" in platform:
            web_page = webdriver.Firefox(options=opt, executable_path=GeckoDriverManager().install())
        else:
            web_page = webdriver.Firefox(options=opt, executable_path=GeckoDriverManager().install())
        web_page.get(BASE_URL)

    except Exception as e:
        reporter("Failed to init FireFox client and get to the page.")
        logging.info(f"Caught and exception while Initializing Browser \n {e}")
        print("\nFailed to init FireFox client and get to the page.")
        web_page.close()

    else:
        logging.info("Finish Initializing Browser")
        return web_page


def validate_punch_in(web_page: webdriver.Firefox) -> None :
    """validating if the daily working hours was successfully added to time card.

    in any case report with image will be sent and log will be taken.
    :param web_page:
    :param working_hours:
    :type web_page: webdriver
    :type working_hours: list[str]
    :return: None
    """
    try:
        # Finding the last added element in order to compare it to the current punch in shift.
        time_card_table = web_page.find_elements(By.CLASS_NAME, "data-row")
        punch_time_row_element = time_card_table[0].find_elements(By.CLASS_NAME, "punch_flex")

    except Exception as e:
        logging.info(f"Caught exception when searching for time card elements. \n {e}")
    else:
        # converting list to strings.
        timeclock_shift_start_time = ", ".join(punch_time_row_element[0].text.replace("/", ".").replace(" ", "").split("\n"))
        timeclock_shift_end_time = ", ".join(punch_time_row_element[1].text.replace("/", ".").replace(" ", "").split("\n"))

        # converting string year format 19.07.22 -> 19.07.2022
        timeclock_shift_start_time = timeclock_shift_start_time.replace("22", strftime('20%y'))
        timeclock_shift_end_time = timeclock_shift_end_time.replace("22", strftime('20%y'))

        # comparing shift info with puched in.
        if (timeclock_shift_start_time == SHIFT_START_TIME) and (timeclock_shift_end_time == SHIFT_END_TIME):
            time_card_table[0].screenshot(f"daily-shift-{strftime('%d.%m.20%y')}.png")
            reporter("Successfully create shifts for today.", f"daily-shift-{strftime('%d.%m.20%y')}.png")
            logging.info(f"shifts for {strftime('%d.%m.20%y')} successfully validated")
        else:
            reporter("Failed to validate your shifts please check them manually.")
            logging.info("Failed to validate your shifts please check them manually.")


def validate_field_write(element: webdriver.Remote._web_element_cls , field_content: str) -> bool:
    """validating if field is filed with the right data, returned true if success.

    :param element: WebElement element that should be inspected.
    :param field_content: The original content the operation trying to insert to field.
    :type element: webdriver
    :type field_content: str
    :rtype: bool
    """
    logging.debug(f"""validating values element: {element.get_dom_attribute("Value")} field_content: {field_content}""")
    return element.get_dom_attribute("Value") == field_content


def field_assert(element: webdriver.Remote._web_element_cls, field_content: str) -> None:
    """Asserting content to field and validating the content is successfully in the field.

    if assertion fails 5 times raises AssertionError.

    :param element: WebElement element that should be inspected.
    :param field_content: The original content the operation trying to insert to field.
    :type element: webdriver.remode.webelement
    :type field_content: str
    :raise AssertionError
    :rtype: None
    """
    for i in range(5):  # trying to assert 5 times
        if not validate_field_write(element, field_content):    # if field_content data not in the field send again.
            sleep(0.1)
            element.send_keys(field_content)
            sleep(0.2)
        else:   # if field_content data can be found in the field break.
            break
    else:   # if the loop running 5 times meaning that the assertion fails and exception should raise.
        logging.info(f"Unable to assert of {field_content} to field name {element.get_dom_attribute('value')}")
        raise AssertionError(f"Unable to assert of {field_content} to field name {element.get_dom_attribute('value')}")


def navigate_to_time_card(web_page: webdriver.Firefox) -> None:
    """
    Gets already logged in live.timeclock365.com panel and only navigates to the time card page.

    :param web_page: WebDriver - already logged-in Firefox page.
    :return: None
    """
    logging.info("Navigating to time card started.")
    try:
        WebDriverWait(web_page, 15).until(EC.presence_of_element_located((By.CLASS_NAME, "first")))
        web_page.get(TIMECARD_URL)
        timecard_elem = WebDriverWait(web_page, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'first')))
        timecard_elem[3].click()

    except Exception as e:
        logging.info(f"Caught and exception while Navigating to time card.\n {e}")
        reporter("Field to navigate to timecard page")
        print(f'Field to navigate to timecard page\n {e}')
        web_page.close()

    logging.info("Finish Navigating to time card.")


def punch_in(web_page: webdriver.Firefox) -> None:
    """
    Gets session on time card page finds punch in and out elements.

    punch in the working hours and calls validation func for reporting the user.
    :param web_page: WebDriver - Time card Firefox page.
    :type web_page: WebDriver
    :rtype: None
    """
    logging.info("Started to punch in time shifts.")
    try:
        # Finding the start and end shift fields.
        start_shift_element, end_shift_element = WebDriverWait(web_page, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "sonata-medium-date")))
    except Exception as e:
        logging.info(f"Caught an exception while punch in time shifts. \n {e}")
        reporter("Can't find start and end shift fields.")
        print(str(e) + "start and end shift fields")
    else:
        # Filling shift start time
        # send keys without validation since was unable to read field value.
        start_shift_element.clear()
        start_shift_element.send_keys(SHIFT_START_TIME)
        # Filling shift end time
        # send keys without validation since was unable to read field value
        end_shift_element.clear()
        end_shift_element.send_keys(SHIFT_END_TIME)


        # Click on the submit button to punch in if OPERATIONAL set to True.
        if OPERATIONAL:
            logging.info("Saving shifts by clicking on the save button.")
            web_page.find_element(By.NAME, "btn_create_and_list").click()
            validate_punch_in(web_page)
        else:
            logging.warning(f"OPERATIONAL flag set to {OPERATIONAL}, note that shift not saved.")
    logging.info("Finish Saving shifts.")


def login(web_page: webdriver.Firefox) -> None:
    """
    Gets Firefox page loaded at BASE_URL and tries to log in to live.timeclock.com

    using the Username and Password form .env file.

    :param web_page: webdriver - Firefox page loaded at BASE_URL.
    :type web_page: webdriver
    :raise Exception: undefinable or unloaded elements.
    :returns: None
    :rtype: None
    """

    logging.info("Start login to timeclock365.com")
    # looking for username field.
    try:
        user_elem = web_page.find_element(By.NAME, "username")
        field_assert(user_elem, USERNAME)
    except Exception as e:
        logging.info(f"Caught and exception while log in \n {e}")
        reporter("Failed to find username field, closing the script")
        web_page.close()
    else:
        user_elem.send_keys(Keys.ENTER)

    # looking for password field.
    try:
        pass_elem = WebDriverWait(web_page, 10, poll_frequency=1).until(EC.presence_of_element_located((By.NAME, "password")))
        sleep(0.5)
        field_assert(pass_elem, PASSWORD)
    except Exception as e:
        logging.info(f"Failed to find password field, closing the script, maybe invalid username \n {e}")
        reporter(f"Failed to find password field, closing the script, maybe invalid username \n {e}")
        web_page.close()
    else:
        web_page.find_element(By.CLASS_NAME, "login-page__submit").click()
    logging.info("Finish login.")


def main():
    logging.basicConfig(filename='./app.log', filemode="w",
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
    logging.info('Starting Auto Punch In Script.')
    web_page = init()
    login(web_page)
    navigate_to_time_card(web_page)
    punch_in(web_page)
    web_page.close()
    logging.info("Task finished.")
    print("Finish punch in.")


if __name__ == '__main__':
    main()
