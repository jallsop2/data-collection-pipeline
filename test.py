
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from time import sleep

def load_and_accept_cookies() -> webdriver.Firefox:
    driver = webdriver.Firefox()
    URL = "https://www.zoopla.co.uk/new-homes/property/london/?q=London&results_sort=newest_listings&search_source=new-homes&page_size=25&pn=1&view_type=list"
    driver.get(URL)
    delay = 10
    sleep(2) # Wait a couple of seconds, so the website doesn't suspect you are a bot
    #try:
    #    driver.switch_to_frame('gdpr-consent-notice') # This is the id of the frame
    #    accept_cookies_button = driver.find_element(by=By.XPATH, value='//*[@id="save"]')
    #    accept_cookies_button.click()

    try:   # If you have the latest version of Selenium, the code above won't run because the "switch_to_frame" is deprecated
        WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.XPATH, '//*[@id="gdpr-consent-notice"]')))
        driver.switch_to.frame('gdpr-consent-notice') # This is the id of the frame
        accept_cookies_button = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.XPATH, '//*[@id="save"]')))
        accept_cookies_button = driver.find_element(by=By.XPATH, value='//*[@id="save"]')
        accept_cookies_button.click()
        driver.switch_to.default_content()

    except:
        pass # If there is no cookies button, we won't find it, so we can pass

    return driver


def get_links(driver: webdriver.Chrome) -> list:

    prop_container = driver.find_element(by=By.XPATH, value='//div[@data-testid="regular-listings"]')
    prop_list = prop_container.find_elements(by=By.XPATH, value='./div')
    link_list = []

    for house_property in prop_list:
        a_tag = house_property.find_element(by=By.TAG_NAME, value='a')
        link = a_tag.get_attribute('href')
        link_list.append(link)

    return link_list

big_list = []
driver = load_and_accept_cookies()

for i in range(5): # The first 5 pages only
    sleep(2)
    print(i)

    try:
        close_button = driver.find_element(by=By.XPATH,value='//button[@data-testid="modal-close"]')
        close_button.click()
    except:
        pass

    big_list.extend(get_links(driver)) # Call the function we just created and extend the big list with the returned list
    page_bar = driver.find_element(by=By.XPATH, value = '//li[@class="css-qhg1xn-PaginationItemPreviousAndNext-PaginationItemNext eaoxhri2"]')
    next_button = page_bar.find_element(by=By.XPATH, value='./a')
    next_button.click()

    


dict_properties = {'Price': [], 'Address': [], 'Bedrooms': [], 'Description': []}

for link in big_list[:10]:

    sleep(1)
    driver.get(link)
    price = driver.find_element(by=By.XPATH, value='//p[@data-testid="price"]').text
    dict_properties['Price'].append(price)
    address = driver.find_element(by=By.XPATH, value='//address[@data-testid="address-label"]').text
    dict_properties['Address'].append(address)
    bedrooms = driver.find_element(by=By.XPATH, value='//div[@class="c-PJLV c-PJLV-iiNveLf-css"]').text
    dict_properties['Bedrooms'].append(bedrooms)
    div_tag = driver.find_element(by=By.XPATH, value='//div[@data-testid="truncated_text_container"]')
    span_tag = div_tag.find_element(by=By.XPATH, value='.//span')
    description = span_tag.text
    dict_properties['Description'].append(description)


    ## TODO: Visit all the links, and extract the data. Don't forget to use sleeps, so the website doesn't suspect
    pass # This pass should be removed once the code is complete

driver.quit() # Close the browser when you finish



print(dict_properties)