import pytest

from pages.home_page import HomePage
from pages.careers_page import CareersPage
from pages.open_positions_page import OpenPositionsPage
from excel_reporter import ExcelReporter


STEPS = [
    "Open Insider home page (insiderone.com)",
    "Accept cookie consent banner",
    "Verify home page URL contains 'insider'",
    "Verify page title contains 'Insider'",
    "Verify navigation bar is visible",
    "Verify hero section is visible",
    "Verify footer section is visible",
    "Navigate to Careers > Quality Assurance page",
    "Click 'See all QA jobs' button",
    "Filter by Location → Istanbul, Turkiye",
    "Filter by Department → Quality Assurance",
    "Wait for filtered job listings to load",
    "Verify at least one job listing is present",
    "Verify all Position fields contain 'Quality Assurance' or 'QA'",
    "Verify all Department fields contain 'Quality Assurance'",
    "Verify all Location fields contain 'Istanbul'",
    "Click 'View Role' on first job listing",
    "Verify redirect to Lever application form (lever.co)",
]


class TestInsiderQA:
    """
    Insider QA Engineer Assessment – End-to-end test scenario.

    Steps:
        1. Visit insiderone.com and verify the home page is opened and
           all main blocks are loaded.
        2. Navigate to QA careers, click "See all QA jobs", filter by
           Location: Istanbul, Turkey and Department: Quality Assurance,
           then verify that the jobs list is present.
        3. Validate each job's Position, Department and Location fields.
        4. Click "View Role" and verify redirection to Lever application form.
    """

    @pytest.fixture(autouse=True)
    def setup(self, driver):
        self.driver = driver
        self.home_page = HomePage(driver)
        self.careers_page = CareersPage(driver)
        self.open_positions_page = OpenPositionsPage(driver)
        self.report = ExcelReporter()
        self.report.add_steps(STEPS)
        yield
        self.report.open_file()

    def test_insider_career_workflow(self):
        step = 0
        try:
            # ── Step 1: Visit Insider home page, verify main blocks ──
            step = 1
            self.home_page.open_home_page()
            self.report.pass_step(1, "Navigated to insiderone.com")

            step = 2
            self.home_page.accept_cookies()
            self.report.pass_step(2, "Cookie banner handled")

            step = 3
            assert self.home_page.is_home_page_opened(), \
                "Insider home page did not open correctly."
            self.report.pass_step(3, f"URL: {self.driver.current_url}")

            step = 4
            page_title = self.home_page.get_page_title()
            assert "Insider" in page_title, \
                f"Page title '{page_title}' does not contain 'Insider'."
            self.report.pass_step(4, f"Title: {page_title}")

            step = 5
            assert self.home_page.is_navbar_displayed(), \
                "Navigation bar is not visible on the home page."
            self.report.pass_step(5, "Navbar element found and visible")

            step = 6
            assert self.home_page.is_hero_section_displayed(), \
                "Hero section is not visible on the home page."
            self.report.pass_step(6, "Hero section element found and visible")

            step = 7
            assert self.home_page.is_footer_displayed(), \
                "Footer section is not visible on the home page."
            self.report.pass_step(7, "Footer element found and visible")

            # ── Step 2: Go to QA careers, click "See all QA jobs", filter ─
            step = 8
            self.careers_page.open_careers_qa_page()
            self.report.pass_step(8, f"URL: {self.driver.current_url}")

            step = 9
            self.careers_page.click_see_all_qa_jobs()
            self.report.pass_step(9, "Clicked 'See all QA jobs' link")

            step = 10
            self.open_positions_page.filter_by_location("Istanbul, Turkiye")
            self.report.pass_step(10, "Selected 'Istanbul, Turkiye' from dropdown")

            step = 11
            self.open_positions_page.filter_by_department("Quality Assurance")
            self.report.pass_step(11, "Selected 'Quality Assurance' from dropdown")

            step = 12
            self.open_positions_page.wait_for_jobs_to_load()
            self.report.pass_step(12, "All visible jobs contain 'Istanbul'")

            step = 13
            jobs_data = self.open_positions_page.get_visible_jobs_data()
            assert len(jobs_data) > 0, \
                "No QA job listings found after filtering."
            self.report.pass_step(13, f"{len(jobs_data)} job listing(s) found")

            # ── Step 3: Verify Position, Department and Location ─────
            step = 14
            for i, job in enumerate(jobs_data):
                # Some listings use "QA" instead of the full phrase.
                assert "Quality Assurance" in job["position"] or "QA" in job["position"], \
                    f"Job #{i+1} position '{job['position']}' invalid."
            positions = ", ".join(j["position"] for j in jobs_data)
            self.report.pass_step(14, positions[:250])

            step = 15
            for i, job in enumerate(jobs_data):
                assert "Quality Assurance" in job["department"], \
                    f"Job #{i+1} department '{job['department']}' invalid."
            self.report.pass_step(15, "All departments = 'Quality Assurance'")

            step = 16
            for i, job in enumerate(jobs_data):
                assert "Istanbul" in job["location"], \
                    f"Job #{i+1} location '{job['location']}' invalid."
            locations = ", ".join(j["location"] for j in jobs_data)
            self.report.pass_step(16, locations[:250])

            # ── Step 4: Click "View Role" → Lever application form ───
            step = 17
            self.open_positions_page.click_view_role(index=0)
            self.report.pass_step(17, "Clicked 'View Role' on first listing")

            step = 18
            self.open_positions_page.navigate_to_lever_page()
            assert self.open_positions_page.is_lever_page(), \
                f"Not on Lever. URL: {self.driver.current_url}"
            self.report.pass_step(18, f"URL: {self.driver.current_url}")

        except Exception as e:
            if step > 0:
                self.report.fail_step(step, str(e)[:250])
            raise
