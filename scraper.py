from datetime import date
from bs4 import BeautifulSoup
import json 
import os 
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


    def get_page_links(self, link_page, num_films = -1):
        """
        Returns a list of links for the webpae of each of the film on this page.
        """

        page = requests.get(link_page)
        html = page.text 
        soup = BeautifulSoup(html, 'html.parser')
        
        film_container = soup.find(name='div', attrs={'class':'lister-list'})
        film_list = film_container.findChildren('div', recursive=False)
        link_list = []

        counter = 0

        for film in film_list:
            film_content = film.find(name='div', attrs={'class':'lister-item-content'})
            a_tag = film_content.find('a')
            
            link_part = a_tag['href']
            link_list.append(f'https://www.imdb.com{link_part}')

            counter += 1
            if counter == num_films:
                break

        return link_list

    def get_film_links(self,num_films):

        films_left = num_films
        page_num = 1
        while True:
            print(f'    Page {page_num}')

            url = f"https://www.imdb.com/search/keyword/?page={page_num}&keywords=superhero&title_type=movie&explore=keywords&mode=detail&ref_=kw_nxt&sort=moviemeter,asc&release_date=%2C2021"
                        
            self.page_link_list.extend(self.get_page_links(url, films_left))

            films_left = num_films - len(self.page_link_list)
            page_num += 1

            if films_left == 0:
                break

    

    def get_page_info(self, link):
        """
        Scrapes the films information from the into a dictionary and adds this the film_dicts attribute.
        """

        film_info = {}

        headers = {'User-Agent': "Mozilla/5.0"}
        page = requests.get(link, headers=headers)
        html = page.text 
        soup = BeautifulSoup(html, 'html.parser')


        film_id = link.split('/')[4]
        film_info['IMDb Id'] = film_id

        
        top_info_container_left = soup.find(name='div', attrs={'class':'sc-80d4314-1 fbQftq'})

        film_name = top_info_container_left.find(name='h1',attrs={'data-testid':"hero-title-block__title"}).text
        film_info['Name'] = film_name

        top_info_list = top_info_container_left.find_all('li',{'class':"ipc-inline-list__item"})
        film_info['Year Released'] = top_info_list[0].find('a').text
        film_info['Age Rating'] = top_info_list[1].find('a').text
        film_info['Length'] = top_info_list[2].text

        top_info_container_right = soup.find('div',{'class':"sc-db8c1937-0 eGmDjE sc-80d4314-3 iBtAhY"})
        film_info['IMDb Rating'] = top_info_container_right.find('span',{'class':"sc-7ab21ed2-1 jGRxWM"}).text

        secondary_container = soup.find('div',{'class':"sc-7643a8e3-10 itwFpV"})
        director_info = secondary_container.find('li',{'data-testid':"title-pc-principal-credit"})
        film_info['Director'] = director_info.find('a').text
        
        details_section = soup.find('section',{'data-testid':"Details"})
        country_section = details_section.find('li',{'data-testid':"title-details-origin"})
        film_info['Country of Origin'] = country_section.find('a').text

        box_office_section = soup.find('div',{'data-testid':"title-boxoffice-section"})
        inner_box_office_section = box_office_section.find('ul')
        box_office_detail_list = inner_box_office_section.findChildren('li', recursive=False)
        film_info['Budget'] = box_office_detail_list[0].find('label').text.split(' ')[0]
        film_info['Gross Profit'] = box_office_detail_list[3].find('label').text

        poster_container = soup.find('div',{'data-testid':"hero-media__poster--inline-video"})
        film_info['Poster Url'] = poster_container.find('img',{'class':"ipc-image"})['src']

        film_info['Date Scraped'] = str(date.today())

        film_info['IMDb Webpage'] = link

        self.film_dicts[film_id] = film_info


    def get_page_images(self, link, num_images, num_images_scraped):

        """
        Locates the pages containing the additional images for the current webpage and saves the images in to a dictionary.

        Args:
            num_images: an integer indicating the maximum number of images the user wants to scrape, if not specified then all images are scraped.
        """

        headers = {'User-Agent': "Mozilla/5.0"}
        page = requests.get(link, headers=headers)
        html = page.text 
        soup = BeautifulSoup(html, 'html.parser')

        date_str = ''.join(str(date.today()).split('-'))
        film_id = link.split('/')[4]
        counter = num_images_scraped+1
        page_image_dict = {}


        thumnail_grid = soup.find('div',{'class':"media_index_thumb_list"})
        image_list = thumnail_grid.findChildren('a', recursive=False)


        for image in image_list:
            print(counter)

            image_src = image.findChildren('img', recursive=False)[0]['src']
            image_data = requests.get(image_src).content
            image_name = f'{date_str}_{film_id}_{counter}.jpg'

            page_image_dict[image_name] = image_data

            if counter == num_images:
                return page_image_dict
            
            counter += 1
        return page_image_dict

        

    def get_film_images(self, link, num_images):

        image_dict = {}

        film_id = link.split('/')[4]

        image_page_url = f'https://www.imdb.com/title/{film_id}/mediaindex'

        headers = {'User-Agent': "Mozilla/5.0"}
        page = requests.get(image_page_url, headers=headers)
        html = page.text 
        soup = BeautifulSoup(html, 'html.parser')

        image_page_span = soup.find('span', {'class':"page_list"})
        image_page_list = image_page_span.findChildren('a', recursive=False)
        num_image_pages = len(image_page_list)+1

        num_images_left = num_images

        for i in range(1,num_image_pages+1):

            page_number_url = f'https://www.imdb.com/title/{film_id}/mediaindex?page={i}'

            image_dict.update(self.get_page_images(page_number_url, num_images_left, len(image_dict)))

            num_images_left = num_images - len(image_dict)

            if num_images_left == 0:
                break

            
        self.film_image_data[film_id] = image_dict


    def scrape_from_link_list(self, get_info = True, get_images = False, num_images = -1):
        """
        Loops through the links in the page_link_list attribute and scrapes the film info in each one.

        Args:
            get_info: A boolean deciding whether to  scrape the film information.
            get_images: A boolean deciding whether to scrape the image data.
            num_images: An integer dictating the number of images scraped.

        """
        counter = 1

        for link in self.page_link_list:
            print(f'    Film {counter}')
            
            
            if get_info == True: 
                self.get_page_info(link)
            
            if get_images == True:
                self.get_film_images(link, num_images= num_images)

            counter += 1


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

    num_films = input('How many films do you want to scrape? ')
    num_images = input('\nHow many images do you want to scrape? ')
    imdb_scraper = scraper()
    
    print('\nScraping links')

    imdb_scraper.get_film_links(num_films)
    print(imdb_scraper.page_link_list)
    #print(len(imdb_scraper.page_link_list))

    print('\nScraping from list:')

    if num_images == 0:
        imdb_scraper.scrape_from_link_list()
    else:
        imdb_scraper.scrape_from_link_list(get_images=True, num_images=num_images)

    print('\nSaving data')

    imdb_scraper.save_info_to_file()

    imdb_scraper.save_images_to_file()

    #print(imdb_scraper.film_dicts)
