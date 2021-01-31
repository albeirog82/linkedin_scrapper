import csv
from parsel import Selector
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import datetime
import json
from langdetect import detect
import requests


linkedin_user = ""
linkedin_pass = ""
target_url = ""

person = {}

writer = csv.writer(open('testing.csv', 'w'))
writer.writerow(['name', 'job_title', 'schools', 'location', 'ln_url'])

driver = webdriver.Chrome('C:/chromedriver_win32/chromedriver.exe')
driver.get('https://www.linkedin.com/')
driver.find_element_by_xpath('//a[text()="Iniciar sesión"]').click()

username_input = driver.find_element_by_name('session_key')
username_input.send_keys(linkedin_user)

password_input = driver.find_element_by_name('session_password')
password_input.send_keys(linkedin_pass)

driver.find_element_by_xpath('//button[text()="Iniciar sesión"]').click()

driver.get('https://www.google.com/')

search_input = driver.find_element_by_name('q')
tech = 'python'
search_input.send_keys('site:linkedin.com/in/ AND "python developer" AND "Bogotá"')

search_input.send_keys(Keys.RETURN)

google_profiles = []
profiles = []
counter = 0

while counter <= 30:
    profiles_page = driver.find_elements_by_xpath('//*[@class="r"]/a[1]')

    try:
        this_profiles = [profile.get_attribute('href') for profile in profiles_page]
        profiles = profiles + this_profiles
    except Exception as e:
        var = 1
    try:
        driver.find_element_by_link_text('Siguiente').click()
    except Exception as e:
        break

    counter = counter + 1

print(len(profiles))

for profile in profiles:
    driver.get(profile)
    try:
        name = ''
        location = ''
        company = ''
        experience_months = 0
        abstract = ''

        source = driver.page_source
        sel = Selector(text=driver.page_source)
        name = sel.xpath('//title/text()').extract_first().split(' | ')[0]
        start = name.find(")")
        name = name[start + 1:].strip()
        job_title = sel.xpath('//h2/text()').extract()

        start_at = job_title[1].find(" at ")
        if start_at == -1:
            start_at = job_title[1].find(" en ")
        company = job_title[1][start_at + 2:].strip()
        strings = []
        start = 0
        correct = ""
        correct_included = {}
        while True:
            start = source.find('{"data"', start)
            end = source.find("</code>", start)
            string = source[start:end]
            if(string.find(company)) > 0:
                correct = string
                correct_dict = json.loads(correct)
                correct_included = correct_dict["included"]
                if len(correct_included) > 0:
                    break
            if end == -1:
                break
            start = end + 1
            strings.append(string)

        works = []
        for key in correct_included:
            try:
                work = {}
                work["title"] = key["title"]
                work["companyName"] = key["companyName"]
                start_date = datetime.datetime(key["dateRange"]["start"]["year"], key["dateRange"]["start"]["month"], 1)
                end_date = 0
                try:
                    end_date = datetime.datetime(key["dateRange"]["end"]["year"], key["dateRange"]["end"]["month"], 1)
                except Exception as e:
                    company = work["companyName"]
                    end_date = datetime.datetime.now()
                experience_months = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)

                work["experience_months"] = experience_months
                works.append(work)
            except Exception as e:
                val = 1

        experience_months = 0
        for key in works:
            experience_months = experience_months + key["experience_months"]

        location = sel.xpath('//*[@class="t-16 t-black t-normal inline-block"]/text()').extract_first().strip()
        company = sel.xpath('//*[@class="text-align-left ml2 t-14 t-black t-bold full-width lt-line-clamp lt-line-clamp--multi-line ember-view"]/text()').extract_first().strip()
        schools = ', '.join(sel.xpath('//*[contains(@class, "pv-entity__school-name")]/text()').extract())
        try:
            see_more_button = driver.find_element_by_link_text('see more').click()
            for elem in driver.find_elements_by_xpath('.//span[@class = "lt-line-clamp__raw-line"]'):
                abstract = abstract + ' ' + elem.text
        except Exception as e:
            for elem in driver.find_elements_by_xpath('.//span[@class = "lt-line-clamp__line lt-line-clamp__line--last"]'):
                abstract = abstract + ' ' + elem.text

        activity = driver.find_elements_by_xpath('.//ul[@class = "pv-recent-activity-section-v2__column-activity list-style-none"]')
        activity_2 = driver.find_elements_by_xpath(
            '//*[@class = "pv-recent-activity-section-v2__column-activity list-style-none"]')
        activity_3 = driver.find_elements_by_xpath(
            '*//ul[@class = "pv-recent-activity-section-v2__column-activity list-style-none"]')

        #Work
        work_data = sel.xpath('//*[@id="bpr-guid-192674"]/text()')
        works = driver.find_elements_by_xpath("//*[@id='bpr-guid-192674']")
        works_2 = sel.xpath("//*[@id='bpr-guid-192674']")
        works_3 = driver.find_elements_by_xpath("//code[@id='bpr-guid-192674']")
        works_4 = driver.find_elements_by_xpath("*//code[@id='bpr-guid-192674']")
        work = sel.xpath('//html/body/div[7]/div[3]/div/div/div/div/div[2]/main/div[6]/div[2]/span/div/section/div[1]/section/ul/li[1]/section/div/div[1]/a/div[2]/h3/text()')

        x = driver.find_element_by_link_text('Contact info')
        x.click()

    except Exception as e:
        print(e)

    person["name"] = name
    person["location"] = location
    person["company"] = company
    person["tech"] = tech
    person["experience"] = experience_months/12
    person["abstract"] = abstract
    person["url"] = profile
    try:
        person["language"] = detect(abstract)
    except Exception as e:
        person["language"] = 'na'

    try:
        x = requests.post(target_url, json=person)
    except Exception as e:
        print(e)
    print(person)

