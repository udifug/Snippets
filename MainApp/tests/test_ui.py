import pytest
from django.urls import reverse
from MainApp.factories import UserFactory
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