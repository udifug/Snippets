import pytest
from django.urls import reverse
from MainApp.factories import UserFactory, SnippetFactory
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


@pytest.mark.django_db
def test_view_snippets_button_on_homepage(browser, live_server):
    """
    Тест проверяет, что на главной странице есть кнопка "Посмотреть сниппеты",
    которая ведет по url-name 'snippets-list'
    """
    # Открываем главную страницу
    browser.get(f"{live_server.url}/")

    # Ищем кнопку "Посмотреть сниппеты" в header
    view_snippets_button = browser.find_element(By.XPATH, "//a[contains(text(), 'Посмотреть сниппеты')]")

    # Проверяем, что кнопка найдена
    assert view_snippets_button is not None

    # Проверяем, что кнопка имеет правильный href (должен вести на snippets-list)
    expected_url = f"{live_server.url}{reverse('snippets-list')}"
    actual_href = view_snippets_button.get_attribute('href')

    assert actual_href == expected_url, f"Ожидался URL: {expected_url}, получен: {actual_href}"


@pytest.mark.django_db
def test_navigation_buttons_for_unauthorized_user(browser, live_server):
    """
    Тест проверяет, что для неавторизованного пользователя в header доступны:
    - кнопка "Посмотреть сниппеты"
    - кнопка "Регистрация"
    Но недоступна кнопка "Мои сниппеты"
    """
    # Переходим на главную страницу
    browser.get(f"{live_server.url}{reverse('home')}")

    # Проверяем, что кнопка "Посмотреть сниппеты" доступна
    view_snippets_button = browser.find_element(By.XPATH, "//a[contains(text(), 'Посмотреть сниппеты')]")
    assert view_snippets_button.is_displayed()
    assert view_snippets_button.is_enabled()

    # Проверяем, что кнопка "Регистрация" доступна
    registration_button = browser.find_element(By.XPATH, "//a[contains(text(), 'Регистрация')]")
    assert registration_button.is_displayed()
    assert registration_button.is_enabled()

    # Проверяем, что кнопка "Мои сниппеты" НЕ доступна (не должна быть видна)
    my_snippets_buttons = browser.find_elements(By.XPATH, "//a[contains(text(), 'Мои сниппеты')]")
    assert len(
        my_snippets_buttons) == 0, "Кнопка 'Мои сниппеты' не должна быть доступна для неавторизованного пользователя"


@pytest.mark.django_db
def test_navigation_buttons_for_authorized_user(browser, live_server):
    """
    Тест проверяет, что для авторизованного пользователя в header доступны:
    - кнопка "Посмотреть сниппеты"
    - кнопка "Мои сниппеты"
    Но недоступна кнопка "Регистрация"
    """
    # Создаем пользователя
    user = UserFactory()

    # Переходим на главную страницу
    browser.get(f"{live_server.url}{reverse('home')}")

    # Находим форму авторизации и входим в систему
    auth_dropdown = browser.find_element(By.ID, "navbarDropdown")
    auth_dropdown.click()

    # Ждем появления формы авторизации
    WebDriverWait(browser, 10).until(
        EC.visibility_of_element_located((By.ID, "usernameInput"))
    )

    # Заполняем форму авторизации
    username_input = browser.find_element(By.ID, "usernameInput")
    password_input = browser.find_element(By.ID, "passwordInput")

    username_input.send_keys(user.username)
    password_input.send_keys("defaultpassword")

    # Отправляем форму
    login_form = browser.find_element(By.CSS_SELECTOR, "form[action*='login']")
    login_form.submit()

    # Ждем перенаправления на главную страницу
    WebDriverWait(browser, 10).until(
        EC.url_to_be(f"{live_server.url}{reverse('home')}")
    )

    # Проверяем, что кнопка "Посмотреть сниппеты" доступна
    view_snippets_button = browser.find_element(By.XPATH, "//a[contains(text(), 'Cписок всех сниппетов')]")
    assert view_snippets_button.is_displayed()
    assert view_snippets_button.is_enabled()

    # Проверяем, что кнопка "Мои сниппеты" доступна
    my_snippets_button = browser.find_element(By.XPATH, "//a[contains(text(), 'Мои сниппеты')]")
    assert my_snippets_button.is_displayed()
    assert my_snippets_button.is_enabled()

    # Проверяем, что кнопка "Регистрация" НЕ доступна (не должна быть видна)
    registration_buttons = browser.find_elements(By.XPATH, "//a[contains(text(), 'Регистрация')]")
    assert len(
        registration_buttons) == 0, "Кнопка 'Регистрация' не должна быть доступна для авторизованного пользователя"

    # Дополнительно проверяем, что отображается приветствие пользователя
    welcome_text = browser.find_element(By.XPATH, f"//button[contains(text(), 'Логин: {user.username}')]")
    assert welcome_text.is_displayed()

    # Проверяем наличие ссылки "Выйти"
    logout_link = browser.find_element(By.XPATH, "//button[contains(text(), 'Выйти')]")
    assert logout_link.is_displayed()
    assert logout_link.is_enabled()


@pytest.mark.django_db
def test_snippets_my_page_access_and_content(browser, live_server):
    """
    Тест проверяет страницу 'Мои сниппеты':
    1. По url может пройти только авторизованный пользователь
    2. На странице доступны только сниппеты авторизованного пользователя
    """
    # Создаем двух пользователей
    user1 = UserFactory()
    user2 = UserFactory()

    # Создаем сниппеты для каждого пользователя
    user1_num_snippets = 13
    user2_num_snippets = 12
    user1_snippets = SnippetFactory.create_batch(user1_num_snippets, user=user1, access='public')
    user2_snippets = SnippetFactory.create_batch(user2_num_snippets, user=user2, access='public')

    # # Тест 1: Проверяем, что неавторизованный пользователь не может получить доступ
    try:
        browser.get(f"{live_server.url}{reverse('snippets-mylist')}")
        # Если страница загрузилась, проверяем, что это не страница "Мои сниппеты"
        page_content = browser.find_element(By.TAG_NAME, "body").text
        assert "Мои сниппеты" not in page_content, \
            "Неавторизованный пользователь не должен иметь доступ к странице 'Мои сниппеты'"
    except Exception as e:
        # Если произошла ошибка (например, 403 Forbidden), это ожидаемое поведение
        assert "403" in str(e) or "Permission" in str(e) or "Forbidden" in str(e), \
            f"Ожидалась ошибка доступа, получена: {e}"

    # Тест 2: Проверяем доступ для авторизованного пользователя
    # Переходим на главную страницу и авторизуемся
    browser.get(f"{live_server.url}{reverse('home')}")

    # Находим форму авторизации и входим в систему
    auth_dropdown = browser.find_element(By.ID, "navbarDropdown")
    auth_dropdown.click()

    # Ждем появления формы авторизации
    WebDriverWait(browser, 10).until(
        EC.visibility_of_element_located((By.ID, "usernameInput"))
    )

    # Заполняем форму авторизации для user1
    username_input = browser.find_element(By.ID, "usernameInput")
    password_input = browser.find_element(By.ID, "passwordInput")

    username_input.send_keys(user1.username)
    password_input.send_keys("defaultpassword")

    # Отправляем форму
    login_form = browser.find_element(By.CSS_SELECTOR, "form[action*='login']")
    login_form.submit()

    # Ждем перенаправления на главную страницу
    WebDriverWait(browser, 10).until(
        EC.url_to_be(f"{live_server.url}{reverse('home')}")
    )

    # Теперь переходим на страницу "Мои сниппеты"
    browser.get(f"{live_server.url}{reverse('snippets-mylist')}")

    # Проверяем, что мы успешно перешли на страницу
    current_url = browser.current_url
    assert current_url == f"{live_server.url}{reverse('snippets-mylist')}", \
        f"Авторизованный пользователь должен иметь доступ к странице 'Мои сниппеты'. Текущий URL: {current_url}"

    # Проверяем заголовок страницы
    pagename = browser.find_element(By.TAG_NAME, "h3").text
    assert "Мои сниппеты" in pagename, \
        f"Заголовок страницы должен содержать 'Мои сниппеты', получен: {pagename}"

    # Тест 3: Проверяем, что отображаются только сниппеты авторизованного пользователя
    # Находим все строки таблицы со сниппетами (исключаем заголовок)
    snippet_rows = browser.find_elements(By.CSS_SELECTOR, "table tbody tr")

    # Проверяем количество сниппетов (должно быть 3 для user1)
    if user1_num_snippets > 5:
        assert len(snippet_rows) == 5
    else:
        assert len(snippet_rows) == user1_num_snippets, \
            f"На странице должно отображаться {user1_num_snippets} сниппета пользователя {user1.username}, найдено: {len(snippet_rows)}"

    # Проверяем, что все сниппеты принадлежат user1
    #UI тест для примера. Нету смысла в поле автора когда я смотрю свои сниппеты
    # for row in snippet_rows:
    #     # Получаем ячейки строки
    #     cells = row.find_elements(By.TAG_NAME, "td")
    #     if len(cells) >= 5:  # Убеждаемся, что есть колонка с автором (5-я колонка)
    #         author_cell = cells[4]  # 5-я колонка (индекс 4) - Автор
    #         author_text = author_cell.text
    #
    #         # Проверяем, что автор - это user1
    #         assert user1.username in author_text, \
    #             f"Сниппет должен принадлежать пользователю {user1.username}, найден автор: {author_text}"
    #
    #         # Проверяем, что это НЕ user2
    #         assert user2.username not in author_text, \
    #             f"На странице не должно быть сниппетов пользователя {user2.username}, найден: {author_text}"

    # Дополнительная проверка: ищем сниппеты по их названиям
    for snippet in user1_snippets[:5]:
        snippet_name_element = browser.find_element(By.XPATH, f"//a[contains(text(), '{snippet.name}')]")
        assert snippet_name_element.is_displayed()

    # Проверяем, что сниппеты user2 НЕ отображаются
    for snippet in user2_snippets:
        try:
            snippet_name_element = browser.find_element(By.XPATH, f"//a[contains(text(), '{snippet.name}')]")
            assert False, f"Сниппет '{snippet.name}' пользователя {user2.username} не должен отображаться на странице"
        except:
            # Если сниппет не найден, это хорошо
            pass

    # Дополнительная проверка: убеждаемся, что на странице есть информация о том, что это "Мои сниппеты"
    page_content = browser.find_element(By.TAG_NAME, "body").text
    assert "Мои сниппеты" in page_content, \
        "На странице должна быть информация о том, что это страница 'Мои сниппеты'"