# Importing the libraries and packages
from selenium import webdriver
from time import sleep
from bs4 import BeautifulSoup
import re
import datetime as dt

'''_____Start of functions_____'''

# Defining a function to clean the words inside the footer buttons of the profile
def name_cleaner(dirty_name):
    return frozenset([ part_name.strip() for part_name in \ 
    		        re.sub(pattern=r'[^a-zA-Z\s]', repl=u'',\
                    	string=dirty_name, flags=re.UNICODE)\
                    	.lower().split(' ') if part_name != '' ])

# Defining a function to clean the study/employment period-related data
def extract_year(text):
    def year(word):
        word = re.findall(r'(\d{4})', text)
        return word
    if 'Present' in text:
        splits = text.split('-')
        data = year(splits[0])[0]
        return [data, 'Present']
    else:
        years = year(text)
        if len(years) == 1:
            # if only 1 date is provided, it means the job started and ended within the same year 
            start = years[0]
            end = years[0]
            return [start, end]
        else:
            return years

footer_params = [['show', 'all', 'experiences'], \
                ['show', 'all', 'education'], \
                ['show', 'all', 'honors', 'awards']]

def url_from_footers(page_source, footer_param):
    footers = page_source.find_all('div', class_ = 'pvs-list__footer-wrapper')
    for footer in footers:
        if (footer.find('div',{'class':'pv2'})):
            footer = footer.find('div',{'class':'pv2'})
            pass
        else:
            footer.find('span', class_='pvs-navigation__text')
            footer_text = footer.get_text()
            cleaned_footer_words = name_cleaner(footer_text)
            if set(text for text in cleaned_footer_words if text!='')==set(footer_param):
                return (footer.find('a')['href'])


# Defining a function to change the format of the time period indicated in the profile
month_to_numbers = { 'Jan':1, 'Feb':2, 'Mar':3, 'Apr':4, 'May':5, 'Jun':6, 'Jul':7, 'Aug':8, 'Sep':9, 'Oct':10, 'Nov':11, 'Dec':12  }

def month_year_str_to_datetime(month_year_str):
    date_list = [ word for word in month_year_str.split(' ') if word!='' ]
    month = month_to_numbers[date_list[0].strip()]
    year = int(date_list[1])
    return dt.datetime(year=year, month=month, day=1)

# Defining a function to get an entire information about work experience from the user's main profile page
def get_experiences_list(exp_page_source):
    boxes = exp_page_source.find_all('div', class_ = 'pvs-entity pvs-entity--padded pvs-list__item--no-padding-in-columns')
    experiences_list = []
    for box in boxes:
        experience_dict = {'company_url' : None, 'position' : None, 'company_name' : None, 'period_of_stay' : None, 'job_location' : None, 'job_description' : None}
        # if there is a pathnode in a work experience showing a position change within the same company
        if (box.find('div', 'display-flex flex-row justify-space-between').a):
            company_name = box.find('div', 'display-flex flex-row justify-space-between').span.text.strip()
            l_span = box.find('div', 'display-flex flex-row justify-space-between').a
            try:
                l_span = box.find('div', 'display-flex flex-row justify-space-between').a
                location = l_span.find('span', 't-14 t-normal t-black--light').span.text.strip()
            except:
                try:
                    l_span = box.find('div', 'pvs-list__outer-container').find('ul').select('li')[-1]
                    location = l_span.find('div', {'class': 'display-flex flex-row justify-space-between'}).find_all('span', {'class': 't-14 t-normal t-black--light'})[1].span.text.strip()
                except :
                    location = None
            first = box.find('div', 'pvs-list__outer-container')
            nodes = first.find_all('div', 'display-flex flex-column full-width align-self-center')
            for node in nodes:
                for b in box.find_all('a', class_='optional-action-target-wrapper display-flex'):
                    experience_dict['company_url'] = b['href']
                i = node.find('div', 'display-flex flex-row justify-space-between')
                position = i.a.div.span.span.text.strip()
                period = i.a.find('span', 't-14 t-normal t-black--light').span.text.strip()
                try:
                    description = node.find('div', 'pvs-list__outer-container').span.text.strip()
                except:
                    description = None
                for item, data in (('position', position), \
                                    ('company_name', company_name), \
                                    ('period_of_stay', period), \
                                    ('start_date', extract_year(period)[0]), \
                                    ('end_date', extract_year(period)[1]), \
                                    ('job_location', location), \
                                    ('job_description', description )):
                    experience_dict[item] = data
                experiences_list.append(experience_dict)
                experience_dict = {}
        # if there are no pathnodes for a different position within the same company
        else:
            for b in box.find_all('a', class_='optional-action-target-wrapper display-flex'):
                experience_dict['company_url'] = b['href']
            for var_name, b in zip(list(experience_dict.keys())[1:], box.find_all('span', class_='visually-hidden')):
                experience_dict[var_name] = b.get_text().split('Â·')[0]
        if experience_dict != {}:
            period = experience_dict['period_of_stay']
            experience_dict['start_date'] = extract_year(period)[0]
            experience_dict['end_date'] = extract_year(period)[1]
        experiences_list.append(experience_dict)
    return experiences_list

# Defining a function to get the entire information about education from the user's main profile page
def get_education_list(edu_page_source):
    boxes = edu_page_source.find_all('div', class_ = 'pvs-entity pvs-entity--padded pvs-list__item--no-padding-in-columns')
    education_list = []
    for box in boxes:
        education_dict = {'university_url' : None, 'university' : None, 'degree' : None, 'study_period' : None, 'grade' : None, 'activities_and_societies' : None}
        for b in box.find_all('a', class_='optional-action-target-wrapper display-flex'):
            education_dict['university_url'] = b['href']
        for var_name, b in zip(list(education_dict.keys())[1:], box.find_all('span', class_='visually-hidden')):
            education_dict[var_name] = b.get_text()
        education_list.append(education_dict)
    return education_list

# Defining a function to get information about honors and awards from the user's main profile page
def get_honorsawards_list(honors_page_source):
    boxes = honors_page_source.find_all('div', class_ = 'pvs-entity pvs-entity--padded pvs-list__item--no-padding-in-columns')
    honorsawards_list = []
    for box in boxes:
        honorsawards_dict = {'honor/award_title' : None, 'issuing_organization_and_date' : None, 'associated_with' : None, 'honor/award_description' : None }
        for var_name, b in zip(list(honorsawards_dict.keys()), box.find_all('span', class_='visually-hidden')):
            honorsawards_dict[var_name] = b.get_text()
        honorsawards_list.append(honorsawards_dict)
    return honorsawards_list
    
''' _____End of functions_____ '''


''' _____Start accessing the profiles using the Selenium's webdriver_____ '''

''' Apply the credentials '''
credentials = open('./data/LinkedIn_login_credentials.txt')
line = credentials.readlines()
username = line[0].strip()
password = line[1].strip()

driver = webdriver.Chrome('./chromedriver')
driver.get('https://www.linkedin.com/login')

''' Key in username '''
email_field = driver.find_element('id', 'username')
email_field.send_keys(username)
print('Finished keying in email.')

''' Key in password '''
password_field = driver.find_element('name', 'session_password')
password_field.send_keys(password)
print('Finished sending the password.')

login_field = driver.find_element('xpath', '//*[@id="organic-div"]/form/div[3]/button')
login_field.click()
# skip_adding_phone = driver.find_element('xpath', '//*[@id='ember459']/button')
# skip_adding_phone.click()
print('Finished logging in.')

''' _____Access and scrape the data of Linkedin profiles_____ '''

footer_params = [['show', 'all', 'experiences'], \
                 ['show', 'all', 'education'], \
                 ['show', 'all', 'honors', 'awards']]

function_choice = {'showallexperiences' : get_experiences_list, \
                   'showalleducation' : get_education_list, \
                   'showallhonorsawards' : get_honorsawards_list}

footer_data = {'showallexperiences' : [], \
               'showalleducation' : [], \
               'showallhonorsawards' : []}

user_profile_data = {}
urls_of_profiles_to_scrape = ['https://www.linkedin.com/in/julietamatevosyan/']
for profile_url in urls_of_profiles_to_scrape:
    driver.get(profile_url)
    sleep(1)
    page_source = BeautifulSoup(driver.page_source, features='html.parser')
    profile_info = page_source.find('div', class_='ph5 pb5')
    profile_name = page_source.find('h1').get_text().strip()
    print(profile_name)
    profile_intro = page_source.find('div', class_= 'text-body-medium break-words').get_text().strip()
    print(profile_intro)
    current_location = page_source.find('span', class_ = 'text-body-small inline t-black--light break-words').get_text().strip()
    print(current_location)
    # the 'user_profile_data' dictionary will store the data of the page after pressing the footer button
    footer_params_failed = []
    url_list = []
    
    for footer_param in footer_params:
        print('The footer param is ----', footer_param) 
        url = url_from_footers(page_source, footer_param)
        print('The url is ----', url)
        
        if url is None:
            print(f'No \'{" ".join(footer_param)}\' footer found!')
            footer_params_failed.append(footer_param)
            continue
        else:
            url_list.append(url)

        print('Now scraping', footer_param, 'expanded section')
        driver.get(url)
        sleep(10)
        footer_page_source = BeautifulSoup(driver.page_source, features='html.parser')
        footer_data[''.join(footer_param)] = function_choice[''.join(footer_param)](footer_page_source)

    # start collecting the work experience data from the profile's main page
    for footer_param in footer_params_failed:
        if footer_param == ['show', 'all', 'experiences']:
            print('Now scraping', footer_param, 'section from the main page')
            experience_tag = page_source.find_all('div', {'id':'experience'}, {'class':'pv-profile-card-anchor'}) 
            if len(experience_tag) > 0 :
                experience_section = experience_tag[0].find_previous('section')
                boxes = experience_section.find_all('li', 'artdeco-list__item pvs-list__item--line-separated pvs-list__item--one-column')
                experiences_list = []
                for box in boxes:
                    experience_dict = {'company_url' : None, 'position' : None, 'company_name' : None, 'period_of_stay' : None, 'job_location' : None, 'job_description' : None}
                    
                    # if there is a pathnode in a work experience showing a position change within the same company 
                    if (box.find('div', 'display-flex flex-row justify-space-between').a):
                        company_tag = box.find('div', 'display-flex flex-row justify-space-between').span
                        company_name = company_tag.text.strip()         
                        try:
                            l_span = box.find('div', 'display-flex flex-row justify-space-between').a
                            location = l_span.find('span', 't-14 t-normal t-black--light').span.text.strip()
                        except:
                            try:
                                l_span = box.find('div', 'pvs-list__outer-container').find('ul').select('li')[-1]
                                location = l_span.find('div', {'class': 'display-flex flex-row justify-space-between'}).find_all('span', {'class': 't-14 t-normal t-black--light'})[1].span.text.strip()
                            except :
                                location = None
                        first = box.find('div', 'pvs-list__outer-container')
                        nodes = first.find_all('div', 'display-flex flex-column full-width align-self-center')
                        for node in nodes:
                            for b in box.find_all('a', class_='optional-action-target-wrapper display-flex'):
                                experience_dict['company_url'] = b['href']
                            i = node.find('div', 'display-flex flex-row justify-space-between')
                            position = i.span.text.strip()
                            period = i.a.find('span', 't-14 t-normal t-black--light').span.text
                            try:
                                description = node.find('div', 'pvs-list__outer-container').span.text.strip()
                            except:
                                description = None
                            for item, data in   (('position', position), \
                                                ('period_of_stay', period), \
                                                ('start_date', extract_year(period)[0]), \
                                                ('end_date', extract_year(period)[1]), \
                                                ('company_name', company_name), \
                                                ('job_location', location), \
                                                ('job_description', description)):
                                experience_dict[item] = data
                            experiences_list.append(experience_dict)
                            experience_dict = {}
                    # if there are no pathnodes for a different position within the same company
                    else:
                        for b in box.find_all('a', class_='optional-action-target-wrapper display-flex'):
                            experience_dict['company_url'] = b['href']
                        for var_name, b in zip(list(experience_dict.keys())[1:],
                                            box.find_all('span', class_='visually-hidden')):
                            experience_dict[var_name] = b.get_text().split('Â·')[0]
                    if experience_dict != {}:
                        period = experience_dict['period_of_stay']
                        experience_dict['start_date'] = extract_year(period)[0]
                        experience_dict['end_date'] = extract_year(period)[1]
                    experiences_list.append(experience_dict)
                footer_data[''.join(footer_param)] = experiences_list
            else:
                print('No Experiences Found')
                user_profile_data[profile_url] = 'No Experiences found'
                continue

        # start collecting education data from the profile's main page
        if footer_param == ['show', 'all', 'education']:
            print('Now scraping', footer_param, 'section from the main page')
            education_element = page_source.find_all('div', {'id':'education'})
            if len(education_element) > 0:
                education_section = education_element[0].find_previous('section')
                boxes = education_section.find_all('li', 'artdeco-list__item pvs-list__item--line-separated pvs-list__item--one-column')
                education_list = []
                for box in boxes:
                    education_dict = {'university_url':None, 'university':None, 'degree':None, 'study_period':None, 'grade':None, 'activities_and_societies':None}
                    for b in box.find_all('a', class_='optional-action-target-wrapper display-flex'):
                        education_dict['university_url'] = b['href']
                    for var_name, b in zip(list(education_dict.keys())[1:], box.find_all('span', class_='visually-hidden')):
                        education_dict[var_name] = b.get_text()
                    education_list.append(education_dict)
                footer_data[''.join(footer_param)] = education_list
            else:
                print('No Education record found')
                user_profile_data[profile_url] = 'No Education record found'
                continue

        # start collecting honors and awards data from the profile's main page
        if footer_param == ['show', 'all', 'honors', 'awards']:
            print('Now scraping', footer_param, 'section from the main page')
            honors_awards_element = page_source.find_all('div', {'id':'honors_and_awards'})
            if len(honors_awards_element) > 0:
                honors_awards_section = honors_awards_element[0].find_previous('section')
                boxes = honors_awards_section.find_all('li', 'artdeco-list__item pvs-list__item--line-separated pvs-list__item--one-column')
                honorsawards_list = []
                for box in boxes:
                    honors_awards_dict = {'honor/award_title': None, 'issuing_organization_and_date': None, 'associated_with': None, 'honor/award_description': None}
                    for var_name, b in zip(list(honors_awards_dict.keys()), box.find_all('span', class_='visually-hidden')):
                        honors_awards_dict[var_name] = b.get_text()
                    honorsawards_list.append(honors_awards_dict)
                footer_data[''.join(footer_param)] = honorsawards_list
            else:
                print('No honors and awards data')
                user_profile_data[profile_url] = 'No honors and awards record found'
    user_profile_data[profile_url] = footer_data

# Closing and quiting the driver
driver.close()
driver.quit()
