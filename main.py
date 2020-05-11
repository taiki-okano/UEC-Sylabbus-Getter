from selenium import webdriver
from getpass import getpass
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from tkinter import filedialog
from time import sleep
import os
import threading


if __name__ == "__main__":

    try:
        with open("classcodes.txt", mode="rt") as fin:
            classcodes = fin.read().split('\n')

    except Exception:
        print("Invalid classcodes")
        quit()

    download_dir = filedialog.askdirectory()

    login_info = dict()

    print("Username: ", end='')
    login_info["username"] = input()

    login_info["password"] = getpass()

    print("2FA Code: ", end='')
    login_info["2FA code"] = input()

    try:
        options = Options()
        options.add_experimental_option("prefs", {
            "plugins.plugins_list": [{"enabled": False,
                                      "name": "Chrome PDF Viewer"}],
            "download.default_directory": download_dir,
            "plugins.always_open_pdf_externally": True
        })

        driver = webdriver.Chrome(options=options)

    except Exception as err:
        print(err)
        print("Failed to start Chrome")
        print("Please install \"webdriver\" for Chrome")
        quit()

    def WaitUntilFullyLoaded(by, value, time=10):
        try:
            element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((by, value))
            )
        except Exception:
            print("Unable to access the page")
            print("Please check the internet connection")
            # driver.quit()
            quit()

        return element

    # Login form (Username and password)

    driver.get("https://campusweb.office.uec.ac.jp/campusweb/")

    WaitUntilFullyLoaded(By.ID, "username")

    username = driver.find_element_by_id("username")
    password = driver.find_element_by_id("password")
    username.send_keys(login_info["username"])
    password.send_keys(login_info["password"])

    login_button = driver.find_element_by_name("_eventId_proceed")
    login_button.click()

    # Login form (2FA)

    WaitUntilFullyLoaded(By.NAME, "authcode")

    authcode = driver.find_element_by_name("authcode")
    authcode.send_keys(login_info["2FA code"])

    proceed_button = driver.find_element_by_name("login")
    proceed_button.click()

    # Download PDF

    def GetSylabbusPDF(classcode):

        sleep(1)

        driver.switch_to.default_content()
        driver.switch_to.frame("menu")

        refer_sylabbus = WaitUntilFullyLoaded(
                By.LINK_TEXT,
                "シラバス参照"
                )
        refer_sylabbus.click()

        sleep(1)

        driver.switch_to.default_content()
        driver.switch_to.frame("body")

        timetable_code_form = WaitUntilFullyLoaded(
                By.ID,
                "jikanwaricd"
                )
        timetable_code_form.send_keys(classcode)
        timetable_code_form.send_keys(Keys.ENTER)

        subject_name = WaitUntilFullyLoaded(
                By.XPATH,
                "/html/body/table[4]/tbody/tr[1]/td"
                )
        subject_name = subject_name.text

        pdf_output_button = WaitUntilFullyLoaded(
                By.XPATH,
                "/html/body/p[2]/input"
                )
        pdf_output_button.click()

        download_button = WaitUntilFullyLoaded(
                By.ID,
                "open-button"
                )
        download_button.click()

        def RenameAfterDownloading():

            while True:
                if "syllabusPdfList.pdf" in os.listdir(download_dir + '/'):
                    break

            sleep(1)

            os.rename(download_dir + "/syllabusPdfList.pdf",
                      download_dir + '/' + subject_name + ".pdf")

        sub_thread = threading.Thread(target=RenameAfterDownloading)
        sub_thread.start()

        driver.switch_to.default_content()
        driver.switch_to.frame("topmenu")

        topmenu_button = WaitUntilFullyLoaded(
                By.XPATH,
                "/html/body/form/table/tbody/tr/td[2]/table/tbody/tr/td[3]/a/i"
                "mg"
                )
        topmenu_button.click()

        sub_thread.join()

    for classcode in classcodes:
        GetSylabbusPDF(classcode)
