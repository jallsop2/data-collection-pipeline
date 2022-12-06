from scraper import scraper
import unittest
import json
import datetime
import os
import sys
import io



class ScraperTestCase(unittest.TestCase):

    def setUp(self):
        text_trap = io.StringIO()
        sys.stdout = text_trap
        self.test_scraper = scraper()    
        

    def test_get_film_links(self):

        self.test_scraper.get_film_links(5)
        output = self.test_scraper.page_link_list
        self.assertIsInstance(output, list)
        self.assertEqual(len(output),5)
        link_template = 'https://www.imdb.com/title'
        self.assertEqual(link_template,output[0][:26])

    def test_get_info(self):
        self.test_scraper.page_link_list = ['https://www.imdb.com/title/tt1825683']
        self.test_scraper.scrape_from_link_list()

        for film_id, film_dict in self.test_scraper.film_dicts.items():
            self.assertIsInstance(film_dict, dict)
            self.assertEqual(film_id,film_dict['IMDb Id'])
            self.assertEqual(len(film_dict),11)

    def test_get_images(self):
        self.test_scraper.page_link_list = ['https://www.imdb.com/title/tt1825683']
        self.test_scraper.scrape_from_link_list(num_images=3)

        for image_dict in self.test_scraper.film_image_data.values():
            self.assertEqual(len(image_dict),3)

    def test_save_info_to_file(self):
        self.test_scraper.film_dicts = {"test_data":{"key 1": "value 1","key 2": "value 2","key 3": "value 3","Poster Url":"https://m.media-amazon.com/images/M/MV5BMTg1MTY2MjYzNV5BMl5BanBnXkFtZTgwMTc4NTMwNDI@._V1_QL75_UX190_CR0,0,190,281_.jpg"}}
        
        datetime_str = datetime.datetime.today().strftime('%Y%m%d_%H%M%S')

        if not os.path.isdir("raw_data"):
            os.makedirs("raw_data")
        
        os.makedirs(f"raw_data/{datetime_str}")
        
        self.test_scraper.save_info_to_file(datetime_str)

        try:
            with open(f"raw_data/{datetime_str}/test_data/data.json") as f:
                return json.load(f)
        except ValueError as e:
            print('Invalid json: %s' % e)

    def tearDown(self):
        sys.stdout = sys.__stdout__




