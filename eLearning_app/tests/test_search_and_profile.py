import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from .factories import *


@pytest.fixture
def browser():
    browser = webdriver.Chrome()
    yield browser
    browser.quit()


@pytest.mark.django_db
def test_search_and_view_profile(browser, live_server):
    # Create test users
    student_user = UserFactory(
        username='john_doe', first_name='John', last_name='Doe')
    student_user.set_password('testpassword')
    student_user.save()
    student = ElearnUserFactory(user=student_user, user_type='student')

    teacher_user = UserFactory(
        username='jane_smith', first_name='Jane', last_name='Smith')
    teacher_user.set_password('testpassword')
    teacher_user.save()
    teacher = ElearnUserFactory(user=teacher_user, user_type='teacher')

    course = CourseFactory(teacher=teacher)
    EnrollmentFactory(student=student, course=course)

    # Login as the student
    browser.get(live_server.url + '/login/')
    username_input = browser.find_element_by_name('username')
    username_input.send_keys('john_doe')
    password_input = browser.find_element_by_name('password')
    password_input.send_keys('testpassword')
    submit_button = browser.find_element_by_css_selector(
        'button[type="submit"]')
    submit_button.click()

    # Wait for the home page to load
    WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.ID, 'container'))
    )

    # **********************
    # Search Scenarios
    # **********************

    # 1. Search by full username
    search_input = browser.find_element_by_name('q')
    search_input.send_keys('john_doe')
    search_button.click()

    WebDriverWait(browser, 10).until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, '#user-search-results .user-card'))
    )
    search_results = browser.find_elements_by_css_selector(
        '#user-search-results .user-card')
    assert len(search_results) == 1
    assert 'john_doe (John Doe) - student' in search_results[0].text

    # 2. Search by partial username (case-insensitive)
    search_input.clear()
    search_input.send_keys('DOE')  # Capitalized
    search_button.click()

    WebDriverWait(browser, 10).until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, '#user-search-results .user-card'))
    )
    search_results = browser.find_elements_by_css_selector(
        '#user-search-results .user-card')
    assert len(search_results) == 1
    assert 'john_doe (John Doe) - student' in search_results[0].text

    # 3. Search by first name
    search_input.clear()
    search_input.send_keys('Jane')
    search_button.click()

    WebDriverWait(browser, 10).until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, '#user-search-results .user-card'))
    )
    search_results = browser.find_elements_by_css_selector(
        '#user-search-results .user-card')
    assert len(search_results) == 1
    assert 'jane_smith (Jane Smith) - teacher' in search_results[0].text

    # 4. Search by last name
    search_input.clear()
    search_input.send_keys('smith')
    search_button.click()

    WebDriverWait(browser, 10).until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, '#user-search-results .user-card'))
    )
    search_results = browser.find_elements_by_css_selector(
        '#user-search-results .user-card')
    assert len(search_results) == 1
    assert 'jane_smith (Jane Smith) - teacher' in search_results[0].text

    # 5. Empty search query
    search_input.clear()
    search_input.send_keys('')
    search_button.click()

    # You might need to adjust this assertion based on how you handle empty queries
    assert 'No users found.' in browser.page_source

    # 6. Search for a non-existent user
    search_input.clear()
    search_input.send_keys('nonexistent_user')
    search_button.click()

    # Again, adjust this based on your implementation
    assert 'No users found.' in browser.page_source

    # **********************
    # Profile View Scenarios
    # **********************

    # 1. View own profile (student)
    browser.get(live_server.url + f'/user/{student_user.id}/')

    WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.ID, 'user-profile'))
    )

    assert browser.current_url == f'{live_server.url}/user/{student_user.id}/'
    assert 'john_doe' in browser.page_source
    assert 'Enrolled Courses' in browser.page_source
    assert course.name in browser.page_source

    # 2. View another user's profile (teacher)
    browser.get(live_server.url + f'/user/{teacher_user.id}/')

    WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.ID, 'user-profile'))
    )

    assert browser.current_url == f'{live_server.url}/user/{teacher_user.id}/'
    assert 'jane_smith' in browser.page_source
    assert 'Courses Taught' in browser.page_source
    assert course.name in browser.page_source

    # 3. Non-existent user profile
    # Assuming 999 is an invalid user ID
    browser.get(live_server.url + '/user/999/')

    # Adjust this assertion based on how you handle 404 errors
    assert 'User not found' in browser.page_source

    # ... Add more tests for privacy settings if implemented
