import logging
import re
from selenium import webdriver
from selenium.common import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import urlparse
from datetime import datetime, timedelta
import time
import unittest


URL = "https://bt2stag.boataround.com"
CHECK_IN = datetime(2024, 6, 1)
class BoataroundTest(unittest.TestCase):
    driver = None
    @classmethod
    def setUpClass(cls):
        op = webdriver.ChromeOptions()
        op.add_argument("--window-size=1200,800")
        cls.driver = webdriver.Chrome(options=op)  # Specify the path to your ChromeDriver
    def test_a_navigate_to_homepage(self):
        driver = self.driver

        # Navigate to the Website
        try:
            self.driver.get(URL)
        except Exception as e:
            logging.info(e)
            self.fail("Error while opening the URL")


        # Verify the homepage loaded successfully
        self.assertIn("Boataround", driver.title)
    def test_b_boataround_order_path(self):
        driver = self.driver

        # Find the destination input element
        try:
            destination_input = WebDriverWait(driver, 5).until(
                EC.visibility_of_element_located((By.ID, "elastic-autocomplete"))
            )
        except TimeoutException:
            self.fail("Timed out waiting for boat list to become visible")
        else:
            # Enter destination "Croatia"
            destination_input.click()

            destination_input.send_keys("Croatia")
            time.sleep(0.6)
            destination_input.send_keys(Keys.RETURN)


        # Calculate dates from saturday to saturday
        first_saturday = CHECK_IN + timedelta(days=(5 - datetime(2024, 6, 1).weekday()) % 7)
        toMonth = first_saturday.strftime("%B")
        second_saturday = datetime.strftime(first_saturday + timedelta(days=7), "%d %b %Y")
        first_saturday = datetime.strftime(first_saturday, "%d %b %Y")
        second_saturday = second_saturday[1::] if second_saturday[0] == '0' else second_saturday
        first_saturday = first_saturday[1::] if first_saturday[0] == '0' else first_saturday
        # Find calendar input
        try:
            monthInput = WebDriverWait(driver, 5).until(
                EC.visibility_of_element_located((By.ID, "calendar-3-input"))
            )
        except TimeoutException:
            self.fail("Timed out waiting for boat list to become visible")
        else:
            # Select the Date on the calendar

            monthInput.click()
            calendar = driver.find_element(By.CLASS_NAME,"calendar-3__months")
            nextMonthBtn = driver.find_element(By.CLASS_NAME, "calendar-3__btn--next")
            currMonth = calendar.find_elements(By.CLASS_NAME, "calendar-3__month-year")[1]
            while not re.match(toMonth, currMonth.text, flags=re.IGNORECASE):
                driver.execute_script("arguments[0].click();", nextMonthBtn)
                time.sleep(0.1)
                currMonth = calendar.find_elements(By.CLASS_NAME, "calendar-3__month-year")[1]

            ci = calendar.find_element(By.XPATH, f"//button[@title='{first_saturday}']")
            driver.execute_script("arguments[0].click();", ci)
            co = calendar.find_element(By.XPATH, f"//button[@title='{second_saturday}']")
            driver.execute_script("arguments[0].click();", co)
            driver.execute_script("arguments[0].click();", co)
            # Handle the overlay dialog
            try:
                dialog = WebDriverWait(driver, 6).until(
                    EC.visibility_of_element_located((By.CLASS_NAME, "overlay-modal-bg"))
                )
            except TimeoutException:
                self.fail("Timed out waiting for boat list to become visible")
            else:
                # Close the overlay dialog
                x = dialog.find_element(By.CLASS_NAME, "overlay-modal__close")
                driver.execute_script("arguments[0].click();", x)

            # Search for the boats
            searchBtn = driver.find_element(By.XPATH, "//button[@value='Search']")
            driver.execute_script("arguments[0].click();", searchBtn)
        finally:
            print("Test B finished.")

    def test_c_select_boat_and_modify_dates(self):
        driver = self.driver

        # Get the search results
        try:
            boatList = WebDriverWait(driver, 10).until(
                EC.visibility_of_all_elements_located((By.CLASS_NAME, "search-result-wrapper"))
            )
        except TimeoutException:
            self.fail("Timed out waiting for boat list to become visible")
        else:
            # Select the second boat from the list and open product page
            link = boatList[1].find_element(By.CLASS_NAME, "search-result")
            driver.execute_script("arguments[0].scrollIntoView(true);", link)

            # Verify CheckIn and CheckOut Dates
            url = urlparse(driver.current_url)
            urllink = urlparse(link.get_attribute("href"))
            params = {x.split("=")[0]:x.split("=")[1] for x in url.query.split("&")}
            linkParams = {x.split("=")[0]:x.split("=")[1] for x in urllink.query.split("&")}
            driver.get(link.get_attribute("href"))
            self.assertEqual(linkParams["checkIn"], params["checkIn"])
            self.assertEqual(linkParams["checkOut"], params["checkOut"])
            self.assertGreaterEqual(len(boatList), 2)

        finally:
            print("Test C Finished")
    def test_d_change_date(self):
        driver = self.driver

        # Change the date on the availability calendar
        try:
            calendar = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.CLASS_NAME, "calendar-section"))
            )
        except TimeoutException:
            self.fail("Timed out waiting for calendar to become visible")
        else:
            time.sleep(1)
            driver.execute_script("arguments[0].scrollIntoView(true);", calendar)
            availablity = driver.find_element(By.CLASS_NAME, "ava-list-wrapper")
            items = availablity.find_elements(By.CSS_SELECTOR, ".ava-item:not(.past)")
            cl = items[len(items)//2]
            time.sleep(1)
            driver.execute_script("console.log(arguments);", items)
            driver.execute_script("arguments[0].click();", cl)
            WebDriverWait(driver, 1)

            # Verify updated checkIn and checkOut params in URL
            dates = cl.find_element(By.CLASS_NAME,"ava-date").text
            [checkIn, checkOut] = ["-".join(x.strip().split('/')[::-1]) for x in dates.split("-")]
            url = urlparse(driver.current_url)
            params = {x.split("=")[0]:x.split("=")[1] for x in url.query.split("&")}

            self.assertEqual(checkIn, params["checkIn"])
            self.assertEqual(checkOut, params["checkOut"])
        finally:
            print("Test D finished.")
    def test_e_reserve_lowest_price_option(self):
        driver = self.driver

        # Get the available reservations
        try:
            reservation = WebDriverWait(driver, 10).until(
                EC.visibility_of_all_elements_located((By.CLASS_NAME, "reservation-box__policies-row"))
            )
        except TimeoutException:
            self.fail("Timed out waiting for reservations list to become visible")
        else:

            # Select the first reservation, which is also the lowest priced
            lowest = reservation[0]
            reserveBtn = lowest.find_element(By.CLASS_NAME,"stateful-button__button")
            driver.execute_script("arguments[0].click();", reserveBtn)
        finally:
            print("Test E finished.")
    def test_f_enter_your_details(self):
        driver = self.driver

        # Check if "Enter Your Details" form exists
        try:
            form = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.XPATH, "//div[@id='form']"))
            )
        except TimeoutException:
                self.fail("Timed out waiting for reservations list to become visible")
        else:
            title = form.find_element(By.CLASS_NAME, "block-heading").text
            time.sleep(1)
            self.assertEqual(title.lower(), "enter your details")
        finally:
            print("Test F finished.")
    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()

if __name__ == "__main__":
    unittest.main()
