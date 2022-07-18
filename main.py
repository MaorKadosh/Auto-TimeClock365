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

        :return WebElement: initiated webdriver with Firefox page loaded with BASE_URL page.
        :rtype: WebElement
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

    :param element: WebElement element that should be inspected.
    :param field_content: The original content the operation trying to insert to field.
    :type element: WebElement
    :type field_content: str
    :rtype: bool
    """
    logging.debug(f"""validating values element: {element.get_dom_attribute("Value")} field_content: {field_content}""")
    return element.get_dom_attribute("Value") == field_content


def field_assert(element, field_content):
    """Asserting content to field and validating the content is successfully in the field.

    if assertion fails 5 times raises AssertionError.

    :param element: WebElement element that should be inspected.
    :param field_content: The original content the operation trying to insert to field.
    :type element: webdriver.remote.webelement
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
        # send keys without validation since was unable to read field value.
        punch_create_elem[0].send_keys(str(strftime("%d.%m.20%y, ") + SHIFT_START_TIME))
        # Filling shift end time
        punch_create_elem[1].clear()
        # send keys without validation since was unable to read field value
        punch_create_elem[1].send_keys(str(strftime("%d.%m.20%y, ") + SHIFT_END_TIME))

        # Click on the submit button to punch in if OPERATIONAL set to True.
        if OPERATIONAL:
            logging.info("Saving shifts by clicking on the save button.")
            web_page.find_element(By.NAME, "btn_create_and_list").click()
    logging.info("Finish Saving shifts.")


def login(web_page):
    """
    Gets Firefox page loaded at BASE_URL and tries to log in to live.timeclock.com

    using the Username and Password form .env file.

    :param web_page: WebElement - Firefox page loaded at BASE_URL.
    :type web_page: WebElement
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
