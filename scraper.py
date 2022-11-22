from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from time import sleep
from datetime import date
import os 
import json 
import requests



class scraper():
    def __init__(self):

        if not os.path.isdir("raw_data"):
            os.makedirs("raw_data")
        
        self.film_dicts = {}

        driver = webdriver.Firefox()
        URL = "https://www.imdb.com/search/keyword/?page=1&keywords=superhero&title_type=movie&explore=keywords&mode=detail&ref_=kw_nxt&sort=moviemeter,asc&release_date=%2C2021"
        driver.get(URL)

        self.link_list = []
        for i in range(2):
            self.link_list.extend(self.get_page_links(driver))
            sleep(0.5)
            self.next_page(driver)

        for link in self.link_list[:3]:
            driver.get(link)
            sleep(0.5)
            self.remove_review_box(driver)
            self.get_info(driver)
            #self.get_images(driver)

        #print(self.film_dicts)

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

        for i in range(5):
            try:
                next_button = driver.find_element(by=By.XPATH, value='//a[@class="lister-page-next next-page"]')
                next_button.click()
                return
            except:
                sleep(0.5)
                print(i)
        
        next_button = driver.find_element(by=By.XPATH, value='//a[@class="lister-page-next next-page"]')
        next_button.click()

    def remove_review_box(self,driver):
        
        try:
            review_prompt = driver.find_element(By.XPATH, '//div[@class="ipc-promptable-base ipc-promptable-dialog ipc-rating-prompt enter-done"]')
            close_button = review_prompt.find_element(By.XPATH, './/button[@title="Close Prompt"]')
            close_button.click()
        
        except:
            pass

    def get_info(self,driver):

        film_info = {}
        delay = 10
        WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.XPATH, '//div[@class="sc-80d4314-1 fbQftq"]')))

        current_url = driver.current_url
        film_id = current_url.split('/')[4]
        film_info['IMDb Id'] = film_id

        top_info_container_left = driver.find_element(By.XPATH, '//div[@class="sc-80d4314-1 fbQftq"]')

        film_name = top_info_container_left.find_element(by=By.XPATH, value='.//h1[@data-testid="hero-title-block__title"]').text
        film_info['Name'] = film_name

        top_info_list = top_info_container_left.find_elements(by=By.XPATH, value='.//li[@class="ipc-inline-list__item"]')
        film_info['Year Released'] = top_info_list[0].find_element(by=By.XPATH, value='.//a').text
        film_info['Age Rating'] = top_info_list[1].find_element(by=By.XPATH, value='.//a').text
        film_info['Length'] = top_info_list[2].text

        top_info_container_right = driver.find_element(By.XPATH, '//div[@class="sc-db8c1937-0 eGmDjE sc-80d4314-3 iBtAhY"]')
        film_info['IMDb Rating'] = top_info_container_right.find_element(By.XPATH, './/span[@class="sc-7ab21ed2-1 jGRxWM"]').text

        secondary_container = driver.find_element(By.XPATH, '//div[@class="sc-7643a8e3-10 itwFpV"]')
        director_info = secondary_container.find_element(By.XPATH, './/li[@data-testid="title-pc-principal-credit"]')
        film_info['Director'] = director_info.find_element(By.XPATH, './/a').text
        
        details_section = driver.find_element(By.XPATH, '//section[@data-testid="Details"]')
        country_section = details_section.find_element(By.XPATH, './/li[@data-testid="title-details-origin"]')
        film_info['Country of Origin'] = country_section.find_element(By.XPATH, './/a').text

        box_office_section = driver.find_element(By.XPATH, '//div[@data-testid="title-boxoffice-section"]')
        box_office_detail_list = box_office_section.find_elements(By.XPATH, './ul/li')
        film_info['Budget'] = box_office_detail_list[0].find_element(By.XPATH, './/label').text.split(' ')[0]
        film_info['Gross Profit'] = box_office_detail_list[3].find_element(By.XPATH, './/label').text

        film_info['Date Scraped'] = str(date.today())

        poster_container = driver.find_element(By.XPATH, '//div[@data-testid="hero-media__poster--inline-video"]')
        poster_url = poster_container.find_element(By.XPATH, './/img[@class="ipc-image"]').get_attribute('src')
        poster_data = requests.get(poster_url).content
        

        if not os.path.isdir("raw_data/"+film_id):
            os.makedirs("raw_data/"+film_id)

        with open(f'raw_data/{film_id}/poster_{film_id}.jpg', 'wb') as file:
            file.write(poster_data)

        film_info['IMDb Webpage'] = 'https://www.imdb.com/title/' + film_id

        self.film_dicts[film_id] = film_info

        

        json_film_info =json.dumps(film_info,indent=4)
        with open(f'raw_data/{film_id}/data.json','w') as file:
            file.write(json_film_info)

    def get_images(self,driver):

        date_list = str(date.today()).split('-')
        date_str = ''
        for i in date_list:
            date_str += i


        current_url = driver.current_url
        film_id = current_url.split('/')[4]

        if not os.path.isdir("raw_data/"+film_id):
            os.makedirs("raw_data/"+film_id)

        if not os.path.isdir("raw_data/"+film_id+'/images'):
            os.makedirs("raw_data/"+film_id+'/images')

        driver.get('https://www.imdb.com/title/'+film_id+'/mediaindex')

        sleep(0.5)

        image_page_span = driver.find_element(By.XPATH, '//span[@class="page_list"]')
        image_page_list = image_page_span.find_elements(By.XPATH, './a')
        num_image_pages = len(image_page_list)+1

        counter = 1

        #for i in range(1,num_image_pages+1):
        for i in range(1,min(3,num_image_pages)):
            delay = 3
            driver.get(f'https://www.imdb.com/title/{film_id}/mediaindex?page={i}')

            sleep(0.5)

            WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.XPATH, '//div[@class="media_index_thumb_list"]')))
            thumnail_grid = driver.find_element(By.XPATH, '//div[@class="media_index_thumb_list"]')
            image_list = thumnail_grid.find_elements(By.XPATH,'./a')

            for image in image_list[:10]:

                image_src = image.find_element(By.XPATH, './img').get_attribute('src')
                image_data = requests.get(image_src).content
                image_name = f'{date_str}_{film_id}_{counter}.jpg'

                with open(f'raw_data/{film_id}/images/{image_name}', 'wb') as file:
                    file.write(image_data)

                counter += 1



        
        




        



if __name__ == '__main__':
    imdb_scraper = scraper()

