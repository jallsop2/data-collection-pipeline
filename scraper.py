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
    """
    The webscraper used to maneuver through a website and scrape data from it.

    Attributes:
        driver: The WebDriver used to move through the webpages.
        film_dicts: A dictionary pairing the film ids with the dictionary of data collected.
        page_link_list: A list of the links to the webpages the data is gotten from.
        film_image_data: A dictionary pairing the film ids with the dictionary of image data collected.

    """
    def __init__(self):
        """
        Initialises the attributes and creates the folder for the data to go in.
        """

        self.film_dicts = {}
        self.page_link_list = []
        self.film_image_data = {}

        self.driver = webdriver.Firefox()
        URL = "https://www.imdb.com/search/keyword/?page=1&keywords=superhero&title_type=movie&explore=keywords&mode=detail&ref_=kw_nxt&sort=moviemeter,asc&release_date=%2C2021"
        self.driver.get(URL)


    def accept_cookies(self):
        """
        Accepts the cookies if the website prompts it.
        """
        
        delay = 10
        sleep(1) 

        try: 
            WebDriverWait(self.driver, delay).until(EC.presence_of_element_located((By.XPATH, '//*[@id="gdpr-consent-notice"]')))
            self.driver.switch_to.frame('gdpr-consent-notice')
            accept_cookies_button = WebDriverWait(self.driver, delay).until(EC.presence_of_element_located((By.XPATH, '//*[@id="save"]')))
            accept_cookies_button = self.driver.find_element(by=By.XPATH, value='//*[@id="save"]')
            accept_cookies_button.click()
            self.driver.switch_to.default_content()

        except:
            pass


    def get_page_links(self):
        """
        Returns a list of links for the webpae of each of the film on this page.
        """

        delay = 10

        WebDriverWait(self.driver, delay).until(EC.presence_of_element_located((By.XPATH, '//div[@class="lister-item-content"]')))
        film_container = self.driver.find_element(by=By.XPATH, value='//div[@class="lister-list"]')
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

    def next_page(self):
        """
        Clicks the next page button.
        """
        delay = 10
        WebDriverWait(self.driver, delay).until(EC.element_to_be_clickable((By.XPATH, '//a[@class="lister-page-next next-page"]')))

        for i in range(5):
            try:
                next_button = self.driver.find_element(by=By.XPATH, value='//a[@class="lister-page-next next-page"]')
                next_button.click()
                return
            except:
                sleep(0.5)
                print(i)
        
        next_button = self.driver.find_element(by=By.XPATH, value='//a[@class="lister-page-next next-page"]')
        next_button.click()

    def remove_review_box(self):
        """
        Closes the prompt to review the film if it appears.
        """
        
        try:
            review_prompt = self.driver.find_element(By.XPATH, '//div[@class="ipc-promptable-base ipc-promptable-dialog ipc-rating-prompt enter-done"]')
            close_button = review_prompt.find_element(By.XPATH, './/button[@title="Close Prompt"]')
            close_button.click()
        
        except:
            pass

    def get_page_info(self):
        """
        Scrapes the films information off the current webpage into a dictionary and adds this the film_dicts attribute.
        """

        film_info = {}
        delay = 10
        WebDriverWait(self.driver, delay).until(EC.presence_of_element_located((By.XPATH, '//div[@class="sc-80d4314-1 fbQftq"]')))

        current_url = self.driver.current_url
        film_id = current_url.split('/')[4]
        film_info['IMDb Id'] = film_id

        top_info_container_left = self.driver.find_element(By.XPATH, '//div[@class="sc-80d4314-1 fbQftq"]')

        film_name = top_info_container_left.find_element(by=By.XPATH, value='.//h1[@data-testid="hero-title-block__title"]').text
        film_info['Name'] = film_name

        top_info_list = top_info_container_left.find_elements(by=By.XPATH, value='.//li[@class="ipc-inline-list__item"]')
        film_info['Year Released'] = top_info_list[0].find_element(by=By.XPATH, value='.//a').text
        film_info['Age Rating'] = top_info_list[1].find_element(by=By.XPATH, value='.//a').text
        film_info['Length'] = top_info_list[2].text

        top_info_container_right = self.driver.find_element(By.XPATH, '//div[@class="sc-db8c1937-0 eGmDjE sc-80d4314-3 iBtAhY"]')
        film_info['IMDb Rating'] = top_info_container_right.find_element(By.XPATH, './/span[@class="sc-7ab21ed2-1 jGRxWM"]').text

        secondary_container = self.driver.find_element(By.XPATH, '//div[@class="sc-7643a8e3-10 itwFpV"]')
        director_info = secondary_container.find_element(By.XPATH, './/li[@data-testid="title-pc-principal-credit"]')
        film_info['Director'] = director_info.find_element(By.XPATH, './/a').text
        
        details_section = self.driver.find_element(By.XPATH, '//section[@data-testid="Details"]')
        country_section = details_section.find_element(By.XPATH, './/li[@data-testid="title-details-origin"]')
        film_info['Country of Origin'] = country_section.find_element(By.XPATH, './/a').text

        box_office_section = self.driver.find_element(By.XPATH, '//div[@data-testid="title-boxoffice-section"]')
        box_office_detail_list = box_office_section.find_elements(By.XPATH, './ul/li')
        film_info['Budget'] = box_office_detail_list[0].find_element(By.XPATH, './/label').text.split(' ')[0]
        film_info['Gross Profit'] = box_office_detail_list[3].find_element(By.XPATH, './/label').text

        poster_container = self.driver.find_element(By.XPATH, '//div[@data-testid="hero-media__poster--inline-video"]')
        film_info['Poster Url'] = poster_container.find_element(By.XPATH, './/img[@class="ipc-image"]').get_attribute('src')

        film_info['Date Scraped'] = str(date.today())

        film_info['IMDb Webpage'] = 'https://www.imdb.com/title/' + film_id

        self.film_dicts[film_id] = film_info


    def scrape_from_link_list(self,num_pages = -1, get_info = True, get_images = False, num_images = -1):
        """
        Loops through the links in the page_link_list attribute and scrapes the film info in each one.

        Args:
            num_pages: An integer indicating how many films info to get. If not specified it gets the information for all of them.
            get_info: A boolean deciding whether to  scrape the film information.
            get_images: A boolean deciding whether to scrape the image data.
            num_images: An integer dictating the number of images scraped.

        """


        if num_pages == -1:
            num_pages = len(self.page_link_list)

        for link in self.page_link_list[:num_pages]:
            self.driver.get(link)
            sleep(0.5)
            self.remove_review_box()

            if get_info == True: 
                self.get_page_info()
            
            if get_images == True:
                self.get_page_images(num_images= num_images)


    def save_info_to_file(self):
        """
        Saves the data in the film_dicts attribute to json files within folders matching the film id.
        """

        if not os.path.isdir("raw_data"):
            os.makedirs("raw_data")

        for film_id, film_info in self.film_dicts.items():

            if not os.path.isdir("raw_data/"+film_id):
                os.makedirs("raw_data/"+film_id)

            poster_data = requests.get(film_info['Poster Url']).content
            with open(f'raw_data/{film_id}/poster_{film_id}.jpg', 'wb') as file:
                file.write(poster_data)
        

            json_film_info =json.dumps(film_info,indent=4)
            with open(f'raw_data/{film_id}/data.json','w') as file:
                file.write(json_film_info)



    def get_page_images(self, num_images = -1):

        """
        Locates the pages containing the additional images for the current webpage and saves the images in to a dictionary.

        Args:
            num_images: an integer indicating the maximum number of images the user wants to scrape, if not specified then all images are scraped.
        """

        
        image_dictionary = {}

        date_str = ''.join(str(date.today()).split('-'))


        current_url = self.driver.current_url
        film_id = current_url.split('/')[4]


        self.driver.get('https://www.imdb.com/title/'+film_id+'/mediaindex')

        sleep(0.5)

        image_page_span = self.driver.find_element(By.XPATH, '//span[@class="page_list"]')
        image_page_list = image_page_span.find_elements(By.XPATH, './a')
        num_image_pages = len(image_page_list)+1


        counter = 1

        for i in range(1,num_image_pages+1):
            delay = 3
            self.driver.get(f'https://www.imdb.com/title/{film_id}/mediaindex?page={i}')

            sleep(0.5)

            WebDriverWait(self.driver, delay).until(EC.presence_of_element_located((By.XPATH, '//div[@class="media_index_thumb_list"]')))
            thumnail_grid = self.driver.find_element(By.XPATH, '//div[@class="media_index_thumb_list"]')
            image_list = thumnail_grid.find_elements(By.XPATH,'./a')

            for image in image_list:

                image_src = image.find_element(By.XPATH, './img').get_attribute('src')
                image_data = requests.get(image_src).content
                image_name = f'{date_str}_{film_id}_{counter}.jpg'

                image_dictionary[image_name] = image_data

                if counter == num_images:
                    self.film_image_data[film_id] = image_dictionary
                    return

                counter += 1
                print(counter)

        
        self.film_image_data[film_id] = image_dictionary

    def save_images_to_file(self):
        """
        Saves the image data in the film_image_data attribute to jpgs in a folder within the film folder for each film.
        """

        if not os.path.isdir("raw_data"):
            os.makedirs("raw_data")

        for film_id, image_dicts in self.film_image_data.items():

            if not os.path.isdir("raw_data/"+film_id):
                os.makedirs("raw_data/"+film_id)

            if not os.path.isdir("raw_data/"+film_id+'/images'):
                os.makedirs("raw_data/"+film_id+'/images')

            for image_name, image_data in image_dicts.items():
                with open(f'raw_data/{film_id}/images/{image_name}', 'wb') as file:
                    file.write(image_data)



if __name__ == '__main__':
    imdb_scraper = scraper()
    
    for i in range(2):
        imdb_scraper.page_link_list.extend(imdb_scraper.get_page_links())
        sleep(0.5)
        imdb_scraper.next_page()

    imdb_scraper.scrape_from_link_list(3, get_images=True, num_images = 10)

    imdb_scraper.save_info_to_file()

    imdb_scraper.save_images_to_file()

    #print(imdb_scraper.film_dicts)

    imdb_scraper.driver.quit()

