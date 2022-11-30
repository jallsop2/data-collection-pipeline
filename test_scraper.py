from scraper import scraper
import unittest
from selenium import webdriver
import json
from time import sleep

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
        #print(self.test_scraper.film_dicts.items())
        for film_id, film_dict in self.test_scraper.film_dicts.items():
            #print(film_id, film_dict)
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


