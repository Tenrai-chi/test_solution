import unittest
import re
import requests

from bs4 import BeautifulSoup
from unittest.mock import Mock, patch
from urllib.parse import unquote

from solution import (process_category_group, get_animals_from_page,
                      get_next_page_url, parse_all_animals, parse_count_animals_string)


class TestProcessCategoryGroup(unittest.TestCase):
    def test_basic_scenario(self):
        """ Тест для основного сценария для связки h3 с ul """

        mock_h3 = Mock()
        mock_h3.text = 'А'
        mock_li1 = Mock()
        mock_li2 = Mock()
        mock_ul = Mock()
        mock_ul.find_all.return_value = [mock_li1, mock_li2]
        mock_category_group = Mock()
        mock_category_group.find_all.return_value = [mock_h3]
        mock_h3.find_next.return_value = mock_ul

        result = process_category_group(mock_category_group)
        self.assertEqual(result, {'А': 2})

    def test_no_h3_elements(self):
        """ Тест, если в category_group нет h3 """

        mock_category_group = Mock()
        mock_category_group.find_all.return_value = []

        result = process_category_group(mock_category_group)

        self.assertEqual(result, {})

    def test_no_ul_element(self):
        """ Тест, если после h3 нет ul """

        mock_h3 = Mock()
        mock_h3.text = 'Б'
        mock_category_group = Mock()
        mock_category_group.find_all.return_value = [mock_h3]
        mock_h3.find_next.return_value = None

        result = process_category_group(mock_category_group)

        self.assertEqual(result, {})


class TestGetAnimalsFromPage(unittest.TestCase):
    @patch('solution.process_category_group')
    def test_no_subcategories(self, mock_process_category_group):
        """ Тест, если на странице нет подкатегорий """

        mock_category_group = Mock()
        mock_category_group.find_parent.return_value = None

        mock_soup = Mock()
        mock_soup.find_all.return_value = [mock_category_group]

        mock_process_category_group.return_value = {'А': 2}
        result = get_animals_from_page(mock_soup)

        self.assertEqual(result, {'А': 2})

    @patch('solution.process_category_group')
    def test_with_subcategories(self, mock_process_category_group):
        """ Тест, когда на странице есть подкатегории """

        mock_category_group_1 = Mock()
        mock_category_group_1.find_parent.return_value = None

        mock_category_group_2 = Mock()
        mock_category_group_2.find_parent.return_value = Mock()
        mock_category_group_2.find_parent.return_value.get.return_value = 'mw-subcategories'

        mock_soup = Mock()
        mock_soup.find_all.return_value = [mock_category_group_1, mock_category_group_2]

        mock_process_category_group.return_value = {'А': 2}
        result = get_animals_from_page(mock_soup)

        self.assertEqual(result, {'А': 2})


class TestGetNextPageURL(unittest.TestCase):
    def test_next_page_exists(self):
        """ Интеграционный тест, если есть следующая страница
            Требует доработки, тк есть возможность, что ссылки на страницы изменятся
        """

        url = 'https://ru.wikipedia.org/w/index.php?title=Категория:Животные_по_алфавиту&pagefrom=Амазонская+моллинезия#mw-pages'
        response = requests.get(url)
        response.raise_for_status()
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')

        expected_url = '/w/index.php?title=Категория:Животные_по_алфавиту&pagefrom=Амфибамус#mw-pages'

        actual_url = get_next_page_url(soup)
        actual_url = unquote(actual_url)

        self.assertEqual(actual_url, expected_url)

    def test_next_page_does_not_exist(self):
        """ Интеграционный тест, если нет следующей страницы
            Требует доработки, тк есть возможность, что ссылки на страницы изменятся
        """

        url = 'https://ru.wikipedia.org/w/index.php?title=Категория:Животные_по_алфавиту&pagefrom=Zygaenoidea#mw-pages'
        response = requests.get(url)
        response.raise_for_status()
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')
        actual_url = get_next_page_url(soup)

        self.assertIsNone(actual_url)


class TestParseCountAnimals(unittest.TestCase):
    def test_get_true_string(self):
        """ Проверяет, что парсится нужная строка с количеством
            записей животных с вики
        """

        string = parse_count_animals_string()
        self.assertIn('Показано 200 страниц из', string)


class TestParseAllAnimals(unittest.TestCase):
    def test_count_animals(self):
        """ Проверяет, что мы действительно обошли весь раздел для парсинга путем сравнения количества
            полученных данных с числом, указанным в вики.
            !!! ДОЛГИЙ ТЕСТ
        """

        string_count_animals = parse_count_animals_string()
        match = re.search(r'из\s*([0-9\s]+),', string_count_animals)
        if match:
            number_with_spaces = match.group(1)
            number = number_with_spaces.replace(' ', '').replace('\xa0', '')

        all_animals = parse_all_animals()
        count_animals = sum(all_animals.values())

        self.assertEqual(int(number), count_animals)
