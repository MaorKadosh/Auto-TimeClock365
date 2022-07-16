import os
import logging
import traceback
from time import sleep
from sys import platform
from time import strftime
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.support import expected_conditions as EC


load_dotenv(".env")
BASE_URL = os.getenv("BASE_URL")
USERNAME = os.getenv("TIME_CLOCK365_USERNAME")
PASSWORD = os.getenv("TIME_CLOCK365_PASSWORD")
os.environ["GH_TOKEN"] = os.getenv("GH_TOKEN")
SHIFT_START_TIME = os.getenv("SHIFT_START_TIME")
SHIFT_END_TIME = os.getenv("SHIFT_END_TIME")
HEADLESS = True if os.getenv("HEADLESS") == 'True' else False
OPERATIONAL = True if os.getenv("OPERATIONAL") == 'True' else False


def reporter(exception):
    pass


def init():
    """
        Init a Selenium base on the OS and loads a web page using .env BASE_URL argument.

        :return webdriver: initiated webdriver with Firefox page loaded with BASE_URL page.
        :rtype: WebDriver
    """
    logging.info("Initializing Browser")
    try:
        opt = Options()
        opt.headless = HEADLESS

        # Check running OS in order to start session correctly.
        if "win32" in platform:
            web_page = webdriver.Firefox(options=opt, executable_path=GeckoDriverManager().install())
        else:
            web_page = webdriver.Firefox(options=opt)
        web_page.get(BASE_URL)

    except Exception as e:
        reporter("Failed to init FireFox client and get to the page.")
        logging.info(f"Caught and exception while Initializing Browser \n {e}")
        print(str(traceback.print_exc()) + "\nFailed to init FireFox client and get to the page.")
        # web_page.close()

    else:
        logging.info("Finish Initializing Browser")
        return web_page


def validate_field_write(element, field_content):
    """validating if field is filed with the right data, returned true if success.

    :param element: WebDriver element that should be inspected.
    :param field_content: The original content the operation trying to insert to field.
    :type element: WebDriver
    :type field_content: str
    :rtype: bool
    """
    logging.debug(f"""validating values element: {element.get_attribute("Value")} field_content: {field_content}""")
    return element.get_attribute("Value") == field_content


def navigate_to_time_card(web_page):
    """
    Gets already logged in live.timeclock365.com panel and only navigates to the time card page.

    :param web_page: WebDriver - already logged-in Firefox page.
    :return: None
    """
    logging.info("Navigating to time card started.")
    try:
        WebDriverWait(web_page, 15).until(EC.presence_of_element_located((By.CLASS_NAME, "first"))).click()
        timecard_elem = WebDriverWait(web_page, 15).until(EC.presence_of_all_elements_located((By.LINK_TEXT, "דיווח נוכחות")))[1]
        timecard_elem.click()
    except Exception as e:
        logging.info(f"Caught and exception while Navigating to time card.\n {e}")
        reporter("Field to navigate to timecard page")
        print(str(e) + "\nField to navigate to timecard page")
        # web_page.close()

    logging.info("Finish Navigating to time card.")


def punch_in(web_page):
    """
    Gets session on time card page finds punch in and out elements.

    :param web_page: WebDriver - Time card Firefox page.
    :type web_page: WebDriver
    :rtype: None
    """
    logging.info("Started to punch in time shifts.")
    try:
        # Finding the start and end shift fields.
        punch_create_elem = web_page.find_elements(By.CLASS_NAME, "sonata-medium-date")
    except Exception as e:
        logging.info(f"Caught an exception while punch in time shifts. \n {e}")
        reporter("Can't find start and end shift fields.")
        print(str(e) + "start and end shift fields")
    else:
        # Filling shift start time
        punch_create_elem[0].clear()
        punch_create_elem[0].send_keys(strftime("%d.%m.20%y, ") + SHIFT_START_TIME)

        # Filling shift end time
        punch_create_elem[1].clear()
        punch_create_elem[1].send_keys(strftime("%d.%m.20%y, ") + SHIFT_END_TIME)

        # Click on the submit button to punch in if OPERATIONAL set to True.
        if OPERATIONAL:
            logging.info("Saving shifts by clicking on the save button.")
            web_page.find_element(By.NAME, "btn_create_and_list").click()
    logging.info("Finish Saving shifts.")


def login(web_page):
    """
    Gets Firefox page loaded at BASE_URL and tries to log in to live.timeclock.com

    using the Username and Password form .env file.

    :param web_page: WebDriver - Firefox page loaded at BASE_URL.
    :type web_page: WebDriver
    :raise Exception: undefinable or unloaded elements.
    :returns: None
    :rtype: None
    """

    # Handling possible exception when not finding username field.
    logging.info("Start login to timecloick365.com")
    try:
        user_elem = web_page.find_element(By.NAME, "username")
    except Exception as e:
        logging.info(f"Caught and exception while log in \n {e}")
        reporter("Failed to find username field, closing the script")
        print(str(e) + "Failed to find username field, closing the script")
        # web_page.close()

    else:
        for i in range(5):
            if not validate_field_write(user_elem, USERNAME):
                user_elem.send_keys(USERNAME)
            else:
                user_elem.send_keys(Keys.ENTER)
                break
        else:
            logging.info(f"Caught an exception while login: unable to fill the username field.")
            raise Exception("Error: Unable to fill username field.")

    # Handling possible exception when finding password field, upon finding filing the password
    try:
        pass_elem = WebDriverWait(web_page, 10, poll_frequency=1).until(EC.presence_of_element_located((By.NAME, "password")))
        sleep(0.5)
    except Exception as e:
        logging.info(f"Failed to find password field, closing the script, maybe invalid username \n {e}")
        reporter(f"Failed to find password field, closing the script, maybe invalid username \n {e}")
        print(str(e) + "Failed to find password field, closing the script, maybe invalid username")
        # web_page.close()

    else:
        for i in range(5):
            if not validate_field_write(pass_elem, PASSWORD):
                pass_elem.send_keys(PASSWORD)
            else:
                web_page.find_element(By.CLASS_NAME, "login-page__submit").click()
                break
        else:
            logging.info("Caught an exception while login: unable to fill the username field.")
            raise Exception("Error: Unable to fill password field.")
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
