import os
import time
import json
from datetime import datetime, timedelta
import boto3
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

# Configure headless Chrome
chrome_options = Options()
chrome_options.add_argument("--headless")  # No UI
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

#driver = webdriver.Chrome("/opt/bin/chromedriver", options=chrome_options)
driver = webdriver.Chrome(options=chrome_options)

# Book the Squash court
def book_court():

    # Login credentials 
    email = 'xxx@gmail.com'
    password = '1234'

    # Define preferred times & courts
    # For each time slot, check all the courts availablity
    PREFERRED_TIMES = ["4:30 PM", "5:00 PM", "6:00 PM"]
    PREFERRED_COURTS = ["Court 3", "Court 4", "Court 2", "Court 1"]

    try:
        # Login to Lifetime website
        driver.get("https://my.lifetime.life/login.html")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "account-username"))).send_keys(email)
        driver.find_element(By.ID, "account-password").send_keys(password)
        driver.find_element(By.ID, "login-btn").click()
        print ('Login successful')
        time.sleep(5)

        # Calculate the booking date (3 days ahead)
        booking_date = (datetime.today() + timedelta(days=3)).strftime('%Y-%m-%d')
        url = f"https://my.lifetime.life/clubs/il/vernon-hills/resource-booking.html?sport=Squash&clubId=183&date={booking_date}&startTime=-1&duration=60&hideModal=true"
        driver.get(url)
        time.sleep(5)

        # Loop through preferred time slots and courts
        for time_slot in PREFERRED_TIMES:
            for court in PREFERRED_COURTS:
                try:
                    print(f"Checking {court} at {time_slot}...")
                    timeslot_xpath = f".//a[.//div[contains(@class, 'timeslot-time') and text()='{time_slot}'] and .//div[contains(@class, 'timeslot-resource') and text()='{court}']]"
                    timeslot = WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.XPATH, timeslot_xpath)))
                    driver.execute_script("arguments[0].click();", timeslot)
                    time.sleep(5)

                    # Accept waiver if prompted
                    try:                                                
                        checkbox = driver.find_element(By.ID, "acceptwaiver")
                        ActionChains(driver).move_to_element(checkbox).click().perform()                        
                        time.sleep(1)
                        
                    except:
                        print("No waiver prompt found.")

                    # Confirm the booking
                    finish_button = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-testid='finishBtn']")))
                    driver.execute_script("arguments[0].click();", finish_button)
                    time.sleep(2)

                    print(f"✅ Successfully booked {court} at {time_slot}. Enjoy your game!")
                    return {"status": "success", "message": f"Booked {court} at {time_slot}."}
                except:
                    print(f"❌ {court} at {time_slot} is not available. Trying next option...")

        print("⚠️ No available courts at preferred times.")
        return {"status": "failed", "message": "No courts available"}

    except Exception as e:
        print(f"🚨 Error occurred: {e}")
        return {"status": "error", "message": str(e)}

    finally:
        driver.quit()

if __name__ == "__main__":
    try:
        book_court()
    except Exception as e:
        print(f"Error occurred: {e}")
    finally:
        driver.quit()