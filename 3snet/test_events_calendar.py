#
# Тесты страницы "Календарь мероприятий"
#

import random
import pytest

from playwright.sync_api import Page, expect
from urllib.parse import quote
from urllib.parse import urljoin


page_URL = "https://dev.3snet.info/eventswidget/"

# Локаторы
listbox_theme_path = '//div[@class="checkselect" and @data-select="Выбрать тематику"]'
theme_template = '//label[@class="custom-checkbox" and input[@name="type"] and span[text()="{THEME}"]]'

listbox_countries_path = '//div[@class="checkselect" and @data-select="Все страны"]'
country_template = '//label[@class="custom-checkbox" and input[@name="country"] and span[text()="{COUNTRY}"]]'

calendar_width_path = 'input[name="width"]'
calendar_height_path = 'input[name="height"]'

header_nav_links_path = '//nav[@class="header-nav"]/ul[@class="nav-menu"]//a'

button_generate_preview = 'button:text("Сгенерировать превью")'

WIDTH_LOWER_LIMIT = 230
WIDTH_UPPER_LIMIT = 1020
HEIGHT_LOWER_LIMIT = 240
HEIGHT_UPPER_LIMIT = 720

PAGE_TIMEOUT = 120000


# Данные
lst_themes = [
    'Выбрать все',
    'Affiliate',
    'Blockchain',
    'Development',
    'Igaming',
    'Internet Marketing',
    'SEO',
    'Финтех',
]

lst_countries = ['Выбрать все']


def get_theme_choices(k=3):
    lst = [x for i, x in enumerate(lst_themes) if i > 0]
    k = min(k, len(lst))
    return random.sample(lst, k)

def get_country_choices(k=3):
    k = min(k, len(lst_countries))
    return random.sample(lst_countries, k)


def select_themes(page: Page, index=None, count=1):
    """
    Открывает выпадающий список 'Выберите тематику'. Выбирает один или несколько элементов
    """
    page.click(listbox_theme_path)
    if index is None:
        for theme in get_theme_choices(count):
            locator = theme_template.format(THEME=theme)
            page.click(locator)
    else:
        if index < 0 or index >= len(lst_themes):
            index = 0
        theme = lst_themes[index]
        locator = theme_template.format(THEME=theme)
        page.click(locator)

    page.click("body")

def select_countries(page: Page, index=None, count=1):
    """
    Открывает выпадающий список 'Выберите страны'. Выбирает несколько элементов
    """
    page.click(listbox_countries_path)
    if index is None:
        for country in get_country_choices(count):
            locator = country_template.format(COUNTRY=country)
            page.click(locator)
    else:
        if index < 0 or index >= len(lst_countries):
            index = 0
        country = lst_countries[index]
        locator = country_template.format(COUNTRY=country)
        page.click(locator)

    page.click("body")


def select_calendar_width(page: Page):
    """
    Выбирает текстовое поле 'Ширина, px'. Вставляет случайное значение в пределах допустимого диапазона
    """
    width = random.randint(WIDTH_LOWER_LIMIT, WIDTH_UPPER_LIMIT)
    page.fill(calendar_width_path, str(width))
    page.click("body")
    return width

def select_calendar_height(page: Page):
    """
    Выбирает текстовое поле 'Высота, px'. Вставляет случайное значение в пределах допустимого диапазона
    """
    height = random.randint(HEIGHT_LOWER_LIMIT, HEIGHT_UPPER_LIMIT)
    page.fill(calendar_height_path, str(height))
    page.click("body")
    return height


def check_iframe_source_valid(context, iframe):
    """
    Проверяет, что ссылка в iframe работает
    """
    iframe_src = iframe.get_attribute("src")
    assert iframe_src, 'В iframe отсутствует атрибут `src`'
    iframe_src = iframe_src.strip()
    
    test_page = context.new_page()
    response = test_page.goto(iframe_src, timeout=PAGE_TIMEOUT, wait_until='domcontentloaded')
    assert response, f'Не удалось загрузить страницу {iframe_src}'
    assert response.status < 400, f'Ошибка HTTP {response.status} при загрузке страницы {iframe_src}'

    # table = test_page.locator('//div[@class="events_wrap_table"]')
    # assert table, 'Некорректная структура в iframe'


def test_calendar_random_valid(page: Page):
    """
    Тестирование виджета "Календарь мероприятий".  
    Параметры:  
        - Выбор тематики: рандомно  
        - Выбор страны: рандомно  
        - Ширина: рандомно  
        - Высота: рандомно  
    """

    page.goto(page_URL, timeout=PAGE_TIMEOUT)

    select_themes(page, count=3)
    select_countries(page, count=3)
    width = select_calendar_width(page)
    height = select_calendar_height(page)

    # Очистка блока превью
    preview = page.locator("#preview")
    preview.evaluate("element => element.innerHTML = ''")

    # Генерация превью
    page.click(button_generate_preview)
    page.wait_for_selector('//div[@id="preview"]/iframe', state="attached", timeout=40000)

    # Проверка содержимого iframe
    preview = page.locator("#preview")
    preview_html = preview.inner_html()
    assert 'iframe' in preview_html, 'Не найден тег iframe'

    iframe = preview.locator("iframe")
    w2 = iframe.get_attribute("width")
    h2 = iframe.get_attribute("height")
    assert width == int(w2 if w2 else 0)
    assert height == int(h2 if h2 else 0)

    check_iframe_source_valid(page.context, iframe)


def test_calendar_list_select_all_valid(page: Page):
    """
    Тестирование виджета "Календарь мероприятий".  
    Параметры:  
        - Выбор тематики: Выбрать все  
        - Выбор страны: Выбрать все  
        - Ширина: рандомно  
        - Высота: рандомно  
    """

    page.goto(page_URL, timeout=PAGE_TIMEOUT)

    select_themes(page, index=0)
    select_countries(page, index=0)
    width = select_calendar_width(page)
    height = select_calendar_height(page)

    # Очистка блока превью
    preview = page.locator("#preview")
    preview.evaluate("element => element.innerHTML = ''")

    # Генерация превью
    page.click(button_generate_preview)
    page.wait_for_selector('//div[@id="preview"]/iframe', state="attached", timeout=40000)

    # Проверка содержимого iframe
    preview = page.locator("#preview")
    preview_html = preview.inner_html()
    assert 'iframe' in preview_html, 'Не найден тег iframe'

    iframe = preview.locator("iframe")
    w2 = iframe.get_attribute("width")
    h2 = iframe.get_attribute("height")
    assert width == int(w2 if w2 else 0)
    assert height == int(h2 if h2 else 0)

    check_iframe_source_valid(page.context, iframe)


def insert_value_and_compare(widget, check_value, expected_value):
    """
    Вставляет значение в указанное поле и сравнивает с ожидаемым значением    
    """
    widget.fill(str(check_value))
    widget.press('Tab')
    widget.page.wait_for_timeout(200)
    x = widget.input_value()
    assert expected_value == int(x if x else 0)


@pytest.mark.parametrize(
    "value, expected_value",
    [
        (WIDTH_LOWER_LIMIT, WIDTH_LOWER_LIMIT),
        (WIDTH_LOWER_LIMIT - 1, WIDTH_LOWER_LIMIT),
        (WIDTH_UPPER_LIMIT, WIDTH_UPPER_LIMIT),
        (WIDTH_UPPER_LIMIT + 1, WIDTH_UPPER_LIMIT),
    ],
    ids=["минимальное валидное", "минимальное невалидное"
         , "максимальное валидное", "максимальное невалидное"]    
)
def test_width_field_accepts_boundary_values(page: Page, value, expected_value):
    """
    Анализ граничных значений для поля "Ширина"
    """
    page.goto(page_URL, timeout=PAGE_TIMEOUT)

    widget = page.locator(calendar_width_path)
    insert_value_and_compare(widget, value, expected_value)


@pytest.mark.parametrize(
    "value, expected_value",
    [
        (0, WIDTH_LOWER_LIMIT),
        (-1, WIDTH_LOWER_LIMIT),
        ('aaa', WIDTH_LOWER_LIMIT),
        ('230px', WIDTH_LOWER_LIMIT),
        ('', WIDTH_LOWER_LIMIT),
        ('   ', WIDTH_LOWER_LIMIT),
        ('999999999', WIDTH_UPPER_LIMIT),
    ],
    ids=["проверка на 0", "проверка отрицательного числа"
         , "проверка букв -ааа", "проверка букв 230px"
         , "ввод пустой строки", "ввод только пробелов"
         , "ввод большого числа"]  
)
def test_width_field_rejects_invalid_values(page: Page, value, expected_value):
    """
    Проверка ввода невалидных значений для поля "Ширина"
    """
    page.goto(page_URL, timeout=PAGE_TIMEOUT)

    widget = page.locator(calendar_width_path)
    insert_value_and_compare(widget, value, expected_value)


@pytest.mark.parametrize(
    "value, expected_value",
    [
        (HEIGHT_LOWER_LIMIT, HEIGHT_LOWER_LIMIT),
        (HEIGHT_LOWER_LIMIT - 1, HEIGHT_LOWER_LIMIT),
        (HEIGHT_UPPER_LIMIT, HEIGHT_UPPER_LIMIT),
        (HEIGHT_UPPER_LIMIT + 1, HEIGHT_UPPER_LIMIT),
    ],
    ids=["минимальное валидное", "минимальное невалидное"
         , "максимальное валидное", "максимальное невалидное"]    
)
def test_height_field_accepts_boundary_values(page: Page, value, expected_value):
    """
    Анализ граничных значений для поля "Высота"
    """
    page.goto(page_URL, timeout=PAGE_TIMEOUT)

    widget = page.locator(calendar_height_path)
    insert_value_and_compare(widget, value, expected_value)


@pytest.mark.parametrize(
    "value, expected_value",
    [
        (0, HEIGHT_LOWER_LIMIT),
        (-1, HEIGHT_LOWER_LIMIT),
        ('aaa', HEIGHT_LOWER_LIMIT),
        ('240px', HEIGHT_LOWER_LIMIT),
        ('', HEIGHT_LOWER_LIMIT),
        ('   ', HEIGHT_LOWER_LIMIT),
        ('999999999', HEIGHT_UPPER_LIMIT),
    ],
    ids=["проверка на 0", "проверка отрицательного числа"
         , "проверка букв -ааа", "проверка букв 230px"
         , "ввод пустой строки", "ввод только пробелов"
         , "ввод большого числа"]  
)
def test_height_field_rejects_invalid_values(page: Page, value, expected_value):
    """
    Проверка ввода невалидных значений для поля "Высота"
    """
    page.goto(page_URL, timeout=PAGE_TIMEOUT)

    widget = page.locator(calendar_height_path)
    insert_value_and_compare(widget, value, expected_value)


def test_header_navigation_links(page: Page):
    """
    Проверка ссылок навигации в главном меню страницы
    """

    page.goto(page_URL, timeout=PAGE_TIMEOUT)

    links = page.locator(header_nav_links_path)
    count = links.count()
    assert count > 0, 'Навигационное меню пустое'
    print('\n')
    
    bad_links = []
    for i in range(count):
        href = links.nth(i).get_attribute('href')
        
        # Пропускаем пустые, якорные или javascript-ссылки
        if not href or href.strip().startswith(('#', 'javascript:')):
            continue

        # Формируем полный URL, если ссылка относительная
        full_url = urljoin(page_URL, href)
        print(f'Проверка ссылки: {full_url}')

        with page.context.new_page() as new_page:
            try:
                response = new_page.goto(full_url, timeout=PAGE_TIMEOUT, wait_until='domcontentloaded')
                if not response:
                    bad_links.append((full_url, f'Не удалось загрузить страницу'))
                    continue
                if response.status >= 400:
                    bad_links.append((full_url, f'Ошибка HTTP {response.status}'))
                    continue
                
                # Проверка 1: страница не пустая и загрузилась
                title = new_page.title()
                if not title:
                    if full_url not in bad_links:
                        bad_links.append((full_url, f'Страница без заголовка'))
                    continue

                # Проверка 2: нет сообщения об ошибке
                body_text = new_page.locator('body').text_content()
                body_text = body_text if body_text else ""

                if '404' in body_text and 'не найден' in body_text.lower():
                    if full_url not in bad_links:
                        bad_links.append((full_url, f'Ошибка 404'))
                        print()

            except Exception as e:
                pytest.fail(f"Ошибка при загрузке ссылки {full_url}: {e}")

    if bad_links:
        text = '\n'.join([f'{url}: {msg}' for url, msg in bad_links])
        text = (f"\nНайдены ошибки при проверке ссылок в главном меню страницы:\n{text}")
        pytest.fail(text)




if __name__ == "__main__":

    # --browser=firefox
    pytest.main([__file__, "--headed", "-v", "-s"])

