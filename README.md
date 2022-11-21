# Data Collection Pipeline

The aim of this project is to implement an industry grade data collection pipelne which can run scalably in the cloud. Using python code to automatically control the browser, extract information from a website and store it on the cloud in a data warehouse and data lake. It shoud conform to industry best pracctices such as being containerised in Docker and running automated tests.

I decided to use the IMDB website because it has a lot of data with clear uses, and each item has a consistent number of attributes attached to it. Specifically I limited myself to superhero movies in order to have a reasonable amount of data. 

# Milestone 3
I started to create the data scraper by defining a class in python, then creating methods to do common tasks such as bypassing cookies and moving to the next page, as well as a method to gather the list of links to the pages for specific films that I wanted. I then called these within the initialiser to automatically collect the links for a certain number of webpages.

This was all done using the selenium python package, which programmatically loads the browser, so it can be instructed to do tasks beyond just getting the static html for  a webpage.

```python
class scraper():
    def __init__(self):

        driver = webdriver.Firefox()
        URL = "https://www.imdb.com/search/keyword/?page=1&keywords=superhero&title_type=movie&explore=keywords&mode=detail&ref_=kw_nxt&sort=moviemeter,asc&release_date=%2C2021"
        driver.get(URL)

        links = []
        for i in range(5):
            print(i)
            links.extend(self.get_page_links(driver))
            sleep(2)
            self.next_page(driver)

        print(links)
        driver.quit()

    def accept_cookies(self,driver):
        
        delay = 10
        sleep(1) 

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

    def get_page_links(self,driver):

        delay = 10

        WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.XPATH, '//div[@class="lister-item-content"]')))
        film_container = driver.find_element(by=By.XPATH, value='//div[@class="lister-list"]')
        film_list = film_container.find_elements(by=By.XPATH, value='./div')
        link_list = []

        for film in film_list:
            film_content = film.find_element(by=By.XPATH, value='.//div[@class="lister-item-content"]')
            #span_tag = film_content.find_element(by=By.XPATH, value='.//span[@class="lister-item-year text-muted unbold"]')
            #film_date = span_tag.text
            #film_date = film_date[1:-1]
            #if film_date != '2022':
            a_tag = film_content.find_element(by=By.XPATH, value='.//a')
            link = a_tag.get_attribute('href')
            link_list.append(link)

        return link_list

    def next_page(self,driver):
        delay = 10
        WebDriverWait(driver, delay).until(EC.element_to_be_clickable((By.XPATH, '//a[@class="lister-page-next next-page"]')))
        next_button = driver.find_element(by=By.XPATH, value='//a[@class="lister-page-next next-page"]')
        next_button.click()

    def remove_review_box(self,driver):
        pass

```