# A Program for Scraping LinkedIn Profiles Using Selenium And Beautiful Soup in Python

This scraper can be used to retrieve information about employment, education, and honors and awards -related information from the publically available Linkedin user profiles.

Information on other profile sections can be retrieved as well by simply adding more functions referring to the already defined functions (i.e. the functions for fetching employment, education, and honors and awards -related data). 

# Notes
- You will need to provide LinkedIn account login and password credentials to access the profiles of other users
- LinkedIn regularly updates the page source which can result in errors while running this program. Usually, this occurs for the footer buttons (that expands a profile section and opens it in a new webpage). The problem can be easily  overcome by inspecting the HTML location of the footer button and updating the 'get_url_from_footers' function on Python script. 
