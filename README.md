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

# Milestone 4

The task for this milestone was to collect the product data from each website, and save to separate json file.

To do this I created a new method which goes to the links scraped from the previous milestone, and takes the neccessary data from them, including the image source for the film poster. This is then saved as a dictionary, which can be converted to a json object using the json library, and saved to a separate json file. The file was created in a separate folder for each film, which were created programatically using the os library a

Each film also has a library of hundreds photos with it, so I also created a method to scrape these images and save them in an images folder within the specific film folders, although each film has hundreds of photots, so it would be very inefficient to store them all.


```python
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
```

# Milestone 5
The aim of this milestone was optimising code, as well as adding docstrings and unit tests to the public methods.

The unit testing was done by creating a test file test_scraper, and using the unittest package, which easily allowes the creation of unit tests. 4 tests were created. Firstly it checks whether the scraper can move to the next page as it should. Next it checks that the get_page_link_list method does in fact return a list. Then it checks that the scrape_from_link_list returns the film data in the expected format as a nested dictionary. Finally it checks that the save_info_to_file function correctly converts and saves the inforamtion as a json file.

```python
class ScraperTestCase(unittest.TestCase):

    def setUp(self):
        self.test_scraper = scraper()    

    def test_next_page(self):
        url = "https://www.imdb.com/search/keyword/?page=1&keywords=superhero&title_type=movie&explore=keywords&mode=detail&ref_=kw_nxt&sort=moviemeter,asc&release_date=%2C2021"
        self.test_scraper.load_link(url)
        sleep(2)
        self.test_scraper.next_page()
        sleep(5)
        next_url = "https://www.imdb.com/search/keyword/?page=2&keywords=superhero&title_type=movie&explore=keywords&mode=detail&ref_=kw_nxt&release_date=%2C2021&sort=moviemeter,asc"
        current_url = self.test_scraper.driver.current_url
        self.assertEqual(next_url,current_url)

    def test_get_page_links(self):
        url = "https://www.imdb.com/search/keyword/?page=1&keywords=superhero&title_type=movie&explore=keywords&mode=detail&ref_=kw_nxt&sort=moviemeter,asc&release_date=%2C2021"
        self.test_scraper.load_link(url)
        sleep(2)
        output = self.test_scraper.get_page_links()
        self.assertIsInstance(output, list)

    def test_get_info(self):
        self.test_scraper.page_link_list = ['https://www.imdb.com/title/tt1825683']
        self.test_scraper.scrape_from_link_list()

        for film_id, film_dict in self.test_scraper.film_dicts.items():
            self.assertIsInstance(film_dict, dict)
            self.assertEqual(film_id,film_dict['IMDb Id'])

    def test_save_info_to_file(self):
        self.test_scraper.film_dicts = {"test_data":{"key 1": "value 1","key 2": "value 2","key 3": "value 3","Poster Url":"https://m.media-amazon.com/images/M/MV5BMTg1MTY2MjYzNV5BMl5BanBnXkFtZTgwMTc4NTMwNDI@._V1_QL75_UX190_CR0,0,190,281_.jpg"}}
        self.test_scraper.save_info_to_file()

        try:
            with open("raw_data/test_data/data.json") as f:
                return json.load(f)
        except ValueError as e:
            print('Invalid json: %s' % e)

    def tearDown(self):
        self.test_scraper.driver.quit()
```

