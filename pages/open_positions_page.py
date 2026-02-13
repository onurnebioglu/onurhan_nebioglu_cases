import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import StaleElementReferenceException

from pages.base_page import BasePage


class OpenPositionsPage(BasePage):
    """Page Object for the Open Positions listing page with filters."""

    URL = "https://insiderone.com/careers/open-positions/"

    
    LOCATION_FILTER = (By.ID, "filter-by-location")
    DEPARTMENT_FILTER = (By.ID, "filter-by-department")

    
    JOBS_LIST = (By.ID, "jobs-list")
    JOB_ITEM = (By.CSS_SELECTOR, ".position-list-item")

    
    JOB_POSITION = (By.CSS_SELECTOR, "p.position-title")
    JOB_DEPARTMENT = (By.CSS_SELECTOR, "span.position-department")
    JOB_LOCATION = (By.CSS_SELECTOR, "div.position-location")

   
    VIEW_ROLE_BTN = (
        By.XPATH,
        ".//a[contains(@class,'btn') and normalize-space()='View Role']",
    )

    def _wait_for_page_ready(self):
        """Wait for the open positions page to fully initialise."""
        WebDriverWait(self.driver, 20).until(
            EC.presence_of_element_located(self.LOCATION_FILTER)
        )
        WebDriverWait(self.driver, 20).until(
            lambda d: len(
                d.find_element(*self.LOCATION_FILTER)
                .find_elements(By.TAG_NAME, "option")
            )
            >= 2
        )

    def _js_select(self, element_id, value):
        """Set a <select> value via JS and dispatch a bubbling change event."""
        self.driver.execute_script("""
            var sel = document.getElementById(arguments[0]);
            sel.value = arguments[1];
            sel.dispatchEvent(new Event('change', {bubbles: true}));
        """, element_id, value)

    def filter_by_location(self, location: str):
        """Select a location from the filter dropdown."""
        self._wait_for_page_ready()
        self._js_select("filter-by-location", location)

        self._wait_for_dom_settle()

    def filter_by_department(self, department: str):
        """Select a department from the filter dropdown."""
        self._js_select("filter-by-department", department)

    def _wait_for_dom_settle(self, interval=0.5, checks=3):
        """Wait until the count of visible job items stabilises across *checks* polls."""
        previous = -1
        stable = 0
        while stable < checks:
            current = len(
                [el for el in self.driver.find_elements(*self.JOB_ITEM) if el.is_displayed()]
            )
            stable = stable + 1 if current == previous else 1
            previous = current
            time.sleep(interval)

    def wait_for_jobs_to_load(self, expected_location="Istanbul"):
        """Wait until visible jobs are filtered and all contain the expected location."""

        def _filtered_correctly(driver):
            data = self._collect_jobs_via_js()
            if not data:
                return False
            return all(expected_location in job["location"] for job in data)

        WebDriverWait(self.driver, 20).until(_filtered_correctly)

    def _collect_jobs_via_js(self):
        """Fast JS helper to read visible job data without stale-element risk."""
        return self.driver.execute_script("""
            var items = document.querySelectorAll('.position-list-item');
            var results = [];
            items.forEach(function(item) {
                if (item.offsetParent !== null) {
                    var title = item.querySelector('p.position-title');
                    var dept  = item.querySelector('span.position-department');
                    var loc   = item.querySelector('div.position-location');
                    results.push({
                        position:   title ? title.textContent.trim() : '',
                        department: dept  ? dept.textContent.trim()  : '',
                        location:   loc   ? loc.textContent.trim()   : ''
                    });
                }
            });
            return results;
        """)

    def get_visible_job_items(self):
        """Return visible job card WebElements using explicit wait + find_elements."""
        WebDriverWait(self.driver, 15).until(
            lambda d: any(el.is_displayed() for el in d.find_elements(*self.JOB_ITEM))
        )
        all_items = self.driver.find_elements(*self.JOB_ITEM)
        return [item for item in all_items if item.is_displayed()]

    def get_visible_jobs_data(self):
        """Collect position, department, location from each visible job card.

        Uses Selenium relative locators (card -> child element) for POM
        compliance. Falls back to a single JS call if a stale reference
        occurs (dynamic DOM).
        """
        try:
            cards = self.get_visible_job_items()
            results = []
            for card in cards:
                results.append({
                    "position": card.find_element(*self.JOB_POSITION).text.strip(),
                    "department": card.find_element(*self.JOB_DEPARTMENT).text.strip(),
                    "location": card.find_element(*self.JOB_LOCATION).text.strip(),
                })
            return results
        except StaleElementReferenceException:
            return self._collect_jobs_via_js()

    def get_jobs_count(self):
        return len(self.get_visible_jobs_data())

    def click_view_role(self, index=0):
        """Click the 'View Role' button inside the visible job card at *index*.

        Uses JS to locate the button inside the nth visible card, avoiding
        stale-element issues when the DOM re-renders between find and click.
        """
        self._handles_before_click = self.driver.window_handles[:]
        self.driver.execute_script("""
            var items = document.querySelectorAll('.position-list-item');
            var visibleIndex = 0;
            for (var i = 0; i < items.length; i++) {
                if (items[i].offsetParent !== null) {
                    if (visibleIndex === arguments[0]) {
                        var btn = items[i].querySelector(
                            "a.btn"
                        );
                        btn.scrollIntoView({block: 'center'});
                        btn.click();
                        return;
                    }
                    visibleIndex++;
                }
            }
        """, index)

    def navigate_to_lever_page(self):
        """Handle redirect to Lever regardless of new-tab or same-tab behaviour."""
        try:
            WebDriverWait(self.driver, 5).until(
                lambda d: len(d.window_handles) > len(self._handles_before_click)
            )
            self.driver.switch_to.window(self.driver.window_handles[-1])
        except Exception:
            pass  # same tab – no switch needed

        WebDriverWait(self.driver, 15).until(EC.url_contains("lever.co"))

    def is_lever_page(self):
        """Check that the current URL belongs to Lever application form."""
        return "lever.co" in self.get_current_url()
