from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import requests
import io
import os
import validators
from bs4 import BeautifulSoup
import time
import sys


# Checks if URL is OK, using validators and requests
# Uses validators to ensure syntax of url is OK
# Uses requests to get http status code
# Returns array with boolean based on status and string describing cause of the error,
# if True is returned, second term is None
# Returns True if:
#   - url was valid
# Returns false if:
#   - request did not return ok http status code
#   - url syntax was incorrect
def check_url(url):
    # Checks URL syntax
    if not validators.url(url):
        return [False, "invalid url syntax"]
    # Checks http status code
    request = requests.get(url)
    if not request.ok:
        return [False, "http status code " + str(request.status_code)]
    # Everything is OK, url is good to use
    else:
        return [True, None]


# Uses requests to download an image as a jpg
# Saves image to specified directory with specified name
# If specified directory does not exist, it is created.
# Returns true if:
#   - url was valid & image was saved successfully
# Returns false if:
#   - request did not return ok http status code
#   - url syntax was incorrect
#   - content is not an image
def download_jpg(image_url, image_name, image_dir, **kwargs):
    # Checks to see if image_dir exits, creates it if it does not
    if not os.path.isdir(image_dir):
        os.mkdir(image_dir)

    url_check = check_url(image_url)
    # Image url is not ok, return false with failure information
    if not url_check[0]:
        return url_check

    image = requests.get(image_url)  # getting image w/ requests
    full_path = image_dir + "/" + image_name + ".jpg"  # Setting the full path and adding .jpg extension

    # Image data request did not yield an image, return false with this information
    if "image" not in image.headers['Content-Type']:
        return [False, "response not an image"]

    # Uses io.open to save image acquired by requests as a file
    with io.open(full_path, 'wb') as file:
        file.write(image.content)
    return [True, None]


# Goes through subcategory pages, getting the links for every individual gun listing
# First iterates through all of the subcategories
# For each subcategory, iterates through every product page in the subcategory,
# using the next button to load the next product page
#   - Stops when next_button is not found, indicating the last product page was found
# For each product page, finds the listings and isolates the links to the listing pages,
# adding those links to the gun_listing_links array
# When all of this is finished, gun_listing_links array is returned
def get_listing_links(subcategory_links, **kwargs):
    gun_listing_links = []
    # Iterates through every subcategory page
    for link in subcategory_links:
        url_check = check_url(link)  # Ensuring url is OK
        # Url was not ok, continue to next subcategory as this one cannot be further traversed
        if not url_check[0]:
            print("[ERROR]: problem retrieving subcategory listings page, " + url_check[1])
            continue
        # Using chromedriver to get the link and initializing it as a BeautifulSoup object
        driver.get(link)
        subcategory_page_html = driver.page_source
        subcategory_page = BeautifulSoup(subcategory_page_html, 'lxml')
        # Html was not properly loaded, continue to next subcategory as this one cannot be further traversed
        if subcategory_page is None:
            print("[ERROR]: problem loading html for subcategory listings page")
            continue
        # Locating listing menu containing listings then finding listings in that menu
        gun_listing_menu = subcategory_page.find(class_="products-grid products-grid--max-4-col")
        # Ensuring listing menu was found. If it is not, next button is used to continue to next page
        if gun_listing_menu is not None:
            gun_listing_list = gun_listing_menu.find_all(class_="item")
            # Ensuring items were found in the listing menu. If not, next button is used to continue to next page
            if gun_listing_list is not None:
                # Isolating links for gun listings, storing them in gun_listing_links array
                for gun_listing in gun_listing_list:
                    gun_listing_unprocessed = gun_listing.find("a", href=True)
                    # Link wasn't found in listing, continue to next listing
                    if gun_listing_unprocessed is None:
                        print("[ERROR]: problem finding link in listing")
                        continue
                    gun_listing_links.append(str(gun_listing_unprocessed).split('"')[3])
            # Error printing when no listings are found
            else:
                print("[ERROR]: problem finding listings in listing menu")
        # Error printing when gun listing menu is not found
        else:
            print("[ERROR]: problem finding listing menu")
        # Iterating over all of the listings in the subcategory
        # Loop continues until next button isn't there
        next_button = subcategory_page.find(class_="next i-next")
        while next_button is not None:
            next_page_link = str(next_button).split('"')[3]
            url_check = check_url(next_page_link)  # Ensuring url is ok
            # Url is not ok, move on to next subcategory as this one cannot be further traversed
            if not url_check[0]:
                print("[ERROR]: problem retrieving subcategory listings page, " + url_check[1])
                break
            # Getting the page pointed to be the next button
            driver.get(next_page_link)
            next_page_html = driver.page_source
            next_page = BeautifulSoup(next_page_html, 'lxml')
            # Html could not be properly loaded, move on to next subcategory as this one cannot be further traversed
            if next_page is None:
                print("[ERROR]: problem loading html for subcategory listings page")
                break
            gun_listing_menu = next_page.find(class_="products-grid products-grid--max-4-col")
            # Ensures listing menu was found. If not, next button is used to continue to next page
            if gun_listing_menu is not None:
                gun_listing_list = gun_listing_menu.find_all(class_="item")
                # Ensures listings are found. If not, next button is used to continue to next page
                if gun_listing_list is not None:
                    # Isolating links for gun listings, storing them in gun_listing_links array
                    for gun_listing in gun_listing_list:
                        gun_listing_unprocessed = gun_listing.find("a", href=True)
                        # Gun listing link was not found, continue to next listing
                        if gun_listing_unprocessed is None:
                            print("[ERROR]: problem finding link in listing")
                            continue
                        gun_listing_links.append(str(gun_listing_unprocessed).split('"')[3])
                # Error printing when no listings are found
                else:
                    print("[ERROR]: problem finding listings in listing menu")
            # Error printing when gun listing menu is not found
            else:
                print("[ERROR]: problem finding listing menu")
            next_button = next_page.find(class_="next i-next")
    return gun_listing_links


# Downloads the first image from every listing
# Iterates through all of the listing links
# For each listing gets the listing page, locates the image link, and downloads the image to the specified directory
# Names images according to image number
# Returns True if:
#   - all images were saved successfully, and the dataset is complete
# Returns False if:
#   - image link wasn't found on listing page
#   - http status code for the image link was not OK
#   - image link did not point to image data
#   - image link was not a valid url
def download_listing_images(listing_links, target_dir, **kwargs):
    success = True
    for link_number in range(len(listing_links)):
        url_check = check_url(listing_links[link_number])  # Ensuring url is OK
        # Url is not OK, continue to next link
        if not url_check[0]:
            success = False
            print("[ERROR]: problem locating listing, " + url_check[1])
            continue
        driver.get(listing_links[link_number])
        listing_page_html = driver.page_source
        listing_page = BeautifulSoup(listing_page_html, 'lxml')
        # Html improperly loaded, continue to next link
        if listing_page is None:
            success = False
            print("[ERROR]: problem loading html for listing")
            continue
        # Locating link to image
        image_link_search = listing_page.find(id="image-main")
        # Image link was not found, continue to next listing link
        if image_link_search is None:
            success = False
            print("[ERROR]: could not locate image link in listing")
            continue
        image_link = str(image_link_search).split('src')[1].split('"')[1]
        download_result = download_jpg(image_url=image_link, image_name=str(link_number), image_dir=target_dir)
        # If download was not successful, success flag is made False and error is printed
        if not download_result[0]:
            success = False
            print("[ERROR]: problem downloading image, " + str(download_result[1]))
    return success


def scrape_category(category_link, subcategories_num, weapon_name, **kwargs):
    # Checking url
    url_check = check_url(category_link)
    # URL is not OK, return False
    if not url_check[0]:
        print("[ERROR]: problem accessing " + weapon_name + " category, " + url_check[1])
        return False
    # Getting page html using chromedriver and initializing it as a BeautifulSoup object
    driver.get(category_link)
    page_html = driver.page_source
    page = BeautifulSoup(page_html, 'lxml')
    # Html was not properly loaded, return False
    if page is None:
        print("[ERROR]: problem loading %s category html" % weapon_name)
        return False
    # Finding the subcategories and storing them in a list
    print("[INFO]: Locating %s subcategories..." % weapon_name)
    subcategories_menu = page.find(id="catList")
    # Could not find subcategories, return False
    if subcategories_menu is None:
        print("[ERROR]: could not find %s subcategories menu" % weapon_name)
        return False
    subcategories_list = subcategories_menu.find_all(class_="item")
    # Could not find items in subcategories menu, return False
    if subcategories_list is None:
        print("[ERROR]: could not find items in %s subcategories menu" % weapon_name)
        return False
    # Isolating and storing in a list links for subcategories, as per the subcategories_num
    subcategories_array = []
    for i in range(subcategories_num):
        subcategory_link_unprocessed = subcategories_list[i].find("a", href=True)
        # Subcategory link could not be found, return False
        if subcategory_link_unprocessed is None:
            print("[ERROR]: could not find link for %s subcategory" % weapon_name)
            return False
        subcategories_array.append(str(subcategory_link_unprocessed).split('"')[1])
    print("[INFO]: Located %s/%s %s subcategories" % (len(subcategories_array), subcategories_num, weapon_name))

    # Gets all of the links to the listings from the subcategory page
    print("[INFO]: Retrieving all %s listing links..." % weapon_name)
    listings_links = get_listing_links(subcategory_links=subcategories_array)
    print("[INFO]: Found %s %s listing links" % (len(listings_links), weapon_name))

    # Tries to download all of the images associated with listings_links
    print("[INFO]: Downloading %s listing images..." % weapon_name)
    if download_listing_images(listing_links=listings_links, target_dir="D:/TSA-2019-Dataset/" + weapon_name):
        print("[INFO]: Successfully downloaded all %s images" % weapon_name)
    else:
        print("[WARNING]: Did not download all %s images, corresponding dataset is incomplete" % weapon_name)
    return True


# Timing start
start = time.time()

# Initializing chromedriver in headless mode
options = Options()
options.headless = True
driver = webdriver.Chrome("chromedriver.exe", options=options)

main_page_url = "https://grabagun.com/firearms.html"

# Checks main page url. If it is unavailable, code execution stops as it is impossible to continue
main_url_check = check_url(main_page_url)
if not main_url_check[0]:
    print("[ERROR]: problem accessing main site, " + main_url_check[1])
    sys.exit()

# Getting main page html using chromedriver and initializing it as a BeautifulSoup object
driver.get(main_page_url)
main_page_html = driver.page_source
main_page = BeautifulSoup(main_page_html, 'lxml')
# Checks to make sure main page html was properly loaded. If not, code execution stops as it is impossible to continue
if main_page is None:
    print("[ERROR]: problem loading html for main site")
    sys.exit()

# Finding the individual gun categories and storing them in a list
print("[INFO]: Locating gun categories...")
categories_menu = main_page.find(id="catList")
# Gun categories menu not found, code execution stops because further traversal is impossible
if categories_menu is None:
    print("[ERROR]: could not find gun categories menu on main page")
    sys.exit()
categories_list = categories_menu.find_all(class_="item")
# No items found in gun categories menu, code execution stops because further traversal is impossible
if categories_list is None:
    print("[ERROR]: could not find items in gun categories menu")
    sys.exit()

# Isolating href link of each category and storing this information in an array
# We are only looking for the first 4 categories, as the last 4 are irrelevant to us
categories_array = []
for i in range(4):
    category_link_unprocessed = categories_list[i].find("a", href=True)
    # One category link not found. Without all 4 categories,
    # continued scraping is pointless, so code execution is stopped
    if category_link_unprocessed is None:
        print("[ERROR]: could not find link in gun category")
        sys.exit()
    categories_array.append(str(category_link_unprocessed).split('"')[1])
print("[INFO]: Located %s/4 gun categories" % len(categories_array))

# Checking to make sure each category was properly scraped
if not scrape_category(category_link=categories_array[0], subcategories_num=3, weapon_name="handgun"):
    print("[WARNING]: handgun category could not be scraped")
if not scrape_category(category_link=categories_array[1], subcategories_num=1, weapon_name="AR-15 AR-10 AK-47"):
    print("[WARNING]: AR-15/AR-10/AK-47 category could not be scraped")
if not scrape_category(category_link=categories_array[2], subcategories_num=5, weapon_name="rifle"):
    print("[WARNING]: rifle category could not be scraped")
if not scrape_category(category_link=categories_array[3], subcategories_num=8, weapon_name="shotgun"):
    print("[WARNING]: shotgun category could not be scraped")

# Shutting down chromedriver
driver.close()

# Timing end and conversion from seconds to h:m:s
end = time.time()
total_seconds = end-start
hours = int(total_seconds/3600)
minutes = int((total_seconds - hours*3600)/60)
seconds = int(total_seconds - (hours*3600 + minutes*60))
print("[INFO]: Data collection process took %s:%s:%s (h:m:s)" % (hours, minutes, seconds))
