from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import time

# Initialize Chrome WebDriver
options = webdriver.ChromeOptions()
options.add_argument("--headless")  # Optional: remove if you want browser to be visible
driver = webdriver.Chrome(options=options)

# Step 1: Open the URL
driver.get("https://www.shl.com/solutions/products/product-catalog/")
wait = WebDriverWait(driver, 15)

# Step 2: Click on the Search Button
search_button_selector = "#Form_FilteringFormJobTitle_action_doFilteringForm > span"
wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, search_button_selector))).click()

# Initialize storage
course_list = []

# Step 3 to 8: Scrape table and paginate
while True:
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "table")))

    # Get all rows
    rows = driver.find_elements(By.CSS_SELECTOR, "table > tbody > tr")

    for row in rows:
        try:
            course_id = row.get_attribute("data-course-id")
            course_name = row.find_element(By.CSS_SELECTOR, "td.custom__table-heading__title > a").text.strip()
            slug = row.find_element(By.CSS_SELECTOR, "td.custom__table-heading__title > a").get_attribute("href").strip()
            keys = [el.text for el in row.find_elements(By.CSS_SELECTOR, "td.product-catalogue__keys .product-catalogue__key")]
            
            course_list.append({
                "course_id": course_id,
                "course_name": course_name,
                "course_url": slug,
                "keys": keys
            })
        except Exception:
            continue

    # Check for next button
    try:
        next_btn = driver.find_element(By.CSS_SELECTOR, "li.pagination__item.-arrow.-next > a")
        if "disabled" in next_btn.get_attribute("class"):
            break
        driver.execute_script("arguments[0].click();", next_btn)
        time.sleep(2)
    except:
        break

# Step 9: Save to JSON
with open("shl_courses2.json", "w", encoding="utf-8") as f:
    json.dump(course_list, f, ensure_ascii=False, indent=4)

driver.quit()
print("✅ Scraping completed. Data saved in shl_courses2.json.")
