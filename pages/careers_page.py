from selenium.webdriver.common.by import By
from pages.base_page import BasePage


class CareersPage(BasePage):
    """Page Object for Insider Careers - Quality Assurance page."""

    URL = "https://insiderone.com/careers/quality-assurance/"

    # Locate by both href and visible text for resilience
    SEE_ALL_QA_JOBS_BTN = (
        By.XPATH,
        "//a[contains(@href,'open-positions') and normalize-space()='See all QA jobs']",
    )

    def open_careers_qa_page(self):
        self.open(self.URL)

    def click_see_all_qa_jobs(self):
        self.scroll_to_element(self.SEE_ALL_QA_JOBS_BTN)
        self.click(self.SEE_ALL_QA_JOBS_BTN)
