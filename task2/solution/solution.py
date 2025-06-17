import csv
import requests
import time

from bs4 import BeautifulSoup
from bs4.element import Tag

BASE_URL = 'https://ru.wikipedia.org'
START_URL = BASE_URL + '/wiki/Категория:Животные_по_алфавиту'


def process_category_group(category_group: Tag) -> dict:
    """ Обрабатывает блок <div class='mw-category-group'> и возвращает словарь
        с количеством животных для каждой буквы из блока
    """

    animals_by_letter = {}

    for h3_element in category_group.find_all('h3'):
        try:
            letter = h3_element.text.strip()[0].upper() if h3_element.text.strip() else None
            if not letter:
                continue

            ul_element = h3_element.find_next('ul')
            if not ul_element:
                continue

            li_elements = ul_element.find_all('li')
            animal_count = len(li_elements)

            animals_by_letter[letter] = animals_by_letter.get(letter, 0) + animal_count

        except Exception as e:
            print(f'Ошибка при обработке h3 в блоке: {e}')
            continue
    return animals_by_letter


def get_animals_from_page(soup: BeautifulSoup) -> dict:
    """ Получает HTML код страницы, ищет блок с буквой и животными
        и возвращает словарь с количеством животных по букве на всей странице.
    """

    animals_by_letter = {}

    category_groups = soup.find_all('div', {'class': 'mw-category-group'})

    # Генератор списка с фильтрацией для исключения подкатегорий mw-subcategories
    filtered_category_groups = [
        group for group in category_groups
        if not group.find_parent('div', {'id': 'mw-subcategories'})
    ]

    # Несмотря на вложенный цикл скорость будет ок, так как категорий с буквами на странице мало, а словарь имеет быстрый доступ
    for category_group in filtered_category_groups:
        group_animals = process_category_group(category_group)

        for letter, count in group_animals.items():
            animals_by_letter[letter] = animals_by_letter.get(letter, 0) + count

    return animals_by_letter


def get_next_page_url(soup: BeautifulSoup) -> str or None:
    """ Парсинг URL следующей страницы из объекта """

    next_page_link = soup.find('a', string='Следующая страница')
    if next_page_link:
        return next_page_link.get('href')


def write_results_to_csv(animals_by_letter: dict) -> None:
    """ Записывает данные из словаря в файл CSV.
        Если файла нет, то создаст его, если есть, то перезапишет
    """

    filename = 'beasts.csv'
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        for letter, count in sorted(animals_by_letter.items()):
            writer.writerow([letter, count])
    print(f'Данные записаны в файл {filename}')


def parse_all_animals() -> dict:
    """ Собирает словарь с количеством животных по всем буквам
        со всех необходимых страниц
    """

    animals_by_letter = {}
    current_url = START_URL
    count_page = 0
    print('Старт обработки...')

    while current_url:
        count_page += 1
        if count_page % 50 == 0:
            print(f'Продолжается обработка, текущая страница: {count_page}')
        try:
            response = requests.get(current_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')

            page_animals_dict = get_animals_from_page(soup)
            for letter, count in page_animals_dict.items():
                animals_by_letter[letter] = animals_by_letter.get(letter, 0) + count

            next_page_url = get_next_page_url(soup)
            if next_page_url:
                current_url = BASE_URL + next_page_url
            else:
                break

            time.sleep(0.25)

        except requests.exceptions.RequestException as e:
            print(f'Ошибка при запросе страницы: {e}')
            break
        except Exception as e:
            print(f'Непредвиденная ошибка: {e}')
            break

    # Просто чтобы было понятно что программа работает
    print(f'Обработано {count_page} страниц')
    return animals_by_letter


def parse_count_animals_string() -> str:
    """ Парсинг строки с количеством статей для теста """

    try:
        response = requests.get(START_URL)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        h2_element = soup.find('h2', string='Страницы в категории «Животные по алфавиту»')

        if h2_element:
            p_element = h2_element.find_next('p')
            if p_element:
                text = ''.join(p_element.find_all(string=True, recursive=False)).strip()

                return text
            else:
                print('Не удалось найти элемент <p> после <h2>.')
        else:
            print('Не удалось найти элемент <h2> с нужным текстом.')

    except requests.exceptions.RequestException as e:
        print(f'Ошибка при загрузке страницы: {e}')
    except AttributeError:
        print('Не удалось найти элементы на странице.')
    except Exception as e:
        print(f'Неожиданная ошибка: {e}')


def main():
    animals_by_letter = parse_all_animals()
    write_results_to_csv(animals_by_letter)


if __name__ == '__main__':
    main()
