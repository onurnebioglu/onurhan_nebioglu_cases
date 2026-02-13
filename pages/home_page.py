from selenium.webdriver.common.by import By
from pages.base_page import BasePage


class HomePage(BasePage):
    """Page Object for Insider home page (https://insiderone.com/)."""

    URL = "https://insiderone.com/"

    
    COOKIE_ACCEPT_BTN = (By.ID, "wt-cli-accept-all-btn")

   
    NAVBAR = (By.ID, "navigation")

   
    HERO_SECTION = (By.CSS_SELECTOR, ".homepage-hero")
    FOOTER = (By.CSS_SELECTOR, "footer")

    def open_home_page(self):
        self.open(self.URL)

    def accept_cookies(self):
        if self.is_displayed(self.COOKIE_ACCEPT_BTN, timeout=5):
            self.click(self.COOKIE_ACCEPT_BTN)

    def is_home_page_opened(self):
        return "insider" in self.get_current_url().lower()

    def is_navbar_displayed(self):
        return self.is_displayed(self.NAVBAR)

    def is_hero_section_displayed(self):
        return self.is_displayed(self.HERO_SECTION)

    def is_footer_displayed(self):
        return self.is_displayed(self.FOOTER)

    def get_page_title(self):
        return self.get_title()
