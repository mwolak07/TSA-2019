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
    # Image url is ok, can proceed to download
    if url_check[0]:
        image = requests.get(image_url)  # getting image w/ requests
        full_path = image_dir + "/" + image_name + ".jpg"  # Setting the full path and adding .jpg extension

        # Makes sure image request data is actually an image
        if "image" in image.headers['Content-Type']:
            # Uses io.open to save image acquired by requests as a file
            with io.open(full_path, 'wb') as file:
                file.write(image.content)
            return [True, None]
        # Response was not an image
        else:
            return [False, "response not an image"]
    # Image url was not ok, return url check results
    else:
        return url_check


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
        # Url was ok, can proceed
        if url_check[0]:
            driver.get(link)
            subcategory_page_html = driver.page_source
            subcategory_page = BeautifulSoup(subcategory_page_html, 'lxml')
            # Checking to make sure html was properly loaded
            if subcategory_page is not None:
                # Iterating over fist page of listings in subcategory
                gun_listing_menu = subcategory_page.find(class_="products-grid products-grid--max-4-col")
                gun_listing_list = gun_listing_menu.find_all(class_="item")
                # Isolating links for gun listings, storing them in gun_listing_links array
                for gun_listing in gun_listing_list:
                    gun_listing_links.append(str(gun_listing.find("a", href=True)).split('"')[3])

                # Iterating over all of the listings in the subcategory
                # Loop continues until next button isn't there
                next_button = subcategory_page.find(class_="next i-next")
                while next_button is not None:
                    next_page_link = str(next_button).split('"')[3]
                    url_check = check_url(next_page_link)  # Ensuring url is ok
                    # Url is ok, can proceed
                    if url_check[0]:
                        driver.get(next_page_link)
                        next_page_html = driver.page_source
                        next_page = BeautifulSoup(next_page_html, 'lxml')
                        # Making sure html was properly loaded
                        if next_page is not None:
                            gun_listing_menu = next_page.find(class_="products-grid products-grid--max-4-col")
                            gun_listing_list = gun_listing_menu.find_all(class_="item")
                            # Isolating links for gun listings, storing them in gun_listing_links array
                            for gun_listing in gun_listing_list:
                                gun_listing_links.append(str(gun_listing.find("a", href=True)).split('"')[3])
                            next_button = next_page.find(class_="next i-next")
                        # Html was not properly loaded, loop is broken out of to not repeatedly check that link
                        else:
                            print("[ERROR]: problem loading html while retrieving listings")
                            break
                    # Url was not ok, error code is printed and loop is broken out of to not repeatedly check same link
                    else:
                        print("[ERROR]: problem retrieving listings, " + url_check[1])
                        break
            # Html was not properly loaded, moves on to next link
            else:
                print("[ERROR]: problem loading html while retrieving listings")
        # Url was not OK, error code is printed and loop continues to next link
        else:
            print("[ERROR]: problem retrieving listings, " + url_check[1])
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
        # Url is OK, can proceed
        if url_check[0]:
            driver.get(listing_links[link_number])
            listing_page_html = driver.page_source
            listing_page = BeautifulSoup(listing_page_html, 'lxml')
            # Checking to make sure html was properly loaded
            if listing_page is not None:
                # Locating link to image
                image_link = str(listing_page.find(id="image-main")).split('src')[1].split('"')[1]
                download_result = download_jpg(image_url=image_link, image_name=str(link_number), image_dir=target_dir)
                # If download was not successful, success flag is made False and error is printed
                if not download_result[0]:
                    success = False
                    print("[ERROR]: problem downloading image, " + str(download_result[1]))
            # Html was not properly loaded, moves on to next image
            else:
                success = False
                print("[ERROR]: problem loading html for listing")
        # Url is not ok, error is printed and loop continues to next url
        else:
            success = False
            print("[ERROR]: problem locating listing, " + url_check[1])
    return success


# Timing start
start = time.time()

# Initializing chromedriver in headless mode
options = Options()
options.headless = True
driver = webdriver.Chrome("chromedriver.exe", options=options)

# Checks main page url. If it is unavailable, code execution stops as it is impossible to continue
main_url_check = check_url("https://grabagun.com/firearms.html")
if not main_url_check[0]:
    print("[ERROR]: problem accessing main site, " + main_url_check[1])
    sys.exit()

# Getting main page html using chromedriver and initializing it as a BeautifulSoup object
driver.get("https://grabagun.com/firearms.html")
main_page_html = driver.page_source
main_page = BeautifulSoup(main_page_html, 'lxml')

# Checks to make sure main page html was properly loaded. If not, code execution stops as it is impossible to continue
if main_page is None:
    print("[ERROR]: problem loading html for main site")
    sys.exit()

# Finding the individual gun categories and storing them in a list
print("[INFO]: Locating gun categories...")
categories_menu = main_page.find(id="catList")
categories_list = categories_menu.find_all(class_="item")

# Isolating href link of each category and storing this information in an array
# We are only looking for the first 4 categories, as the last 4 are irrelevant to us
categories_array = []
for i in range(4):
    categories_array.append(str(categories_list[i].find("a", href=True)).split('"')[1])
print("[INFO]: Located %s/4 gun categories" % len(categories_array))

# Checking handgun url
handgun_url_check = check_url(categories_array[0])
# Handgun url is OK, can continue scraping
if handgun_url_check[0]:
    # Getting handgun page html using chromedriver and initializing it as a BeautifulSoup object
    driver.get(categories_array[0])
    handgun_page_html = driver.page_source
    handgun_page = BeautifulSoup(handgun_page_html, 'lxml')
    # Checking to make sure html was properly loaded
    if handgun_page is not None:
        # Finding the handgun subcategories and storing them in a list
        print("[INFO]: Locating handgun subcategories...")
        handgun_subcategories_menu = handgun_page.find(id="catList")
        handgun_subcategories_list = handgun_subcategories_menu.find_all(class_="item")

        # Isolating and storing in a list links for handgun subcategories, we are only interested in the first 3
        handgun_subcategories_array = []
        for i in range(3):
            handgun_subcategories_array.append(str(handgun_subcategories_list[i].find("a", href=True)).split('"')[1])
        print("[INFO]: Located %s/3 handgun subcategories" % len(handgun_subcategories_array))

        # Gets all of the links to the handgun listings from the subcategory page
        print("[INFO]: Retrieving all handgun listing links...")
        handgun_listings_links = get_listing_links(subcategory_links=handgun_subcategories_array)
        print("[INFO]: Found %s handgun listing links" % len(handgun_listings_links))

        # Tries to download all of the images associated with handgun_listings_links
        print("[INFO]: Downloading handgun listing images...")
        if download_listing_images(listing_links=handgun_listings_links, target_dir="D:/TSA-2019-Dataset/Handguns"):
            print("[INFO]: Successfully downloaded all handgun images")
        else:
            print("[WARNING]: Did not download all handgun images, handgun dataset is incomplete")
    # Html was not properly loaded, next category is scraped
    else:
        print("[ERROR]: problem loading handgun category html")
# Handgun url was not ok, error is printed and next category is scraped
else:
    print("[ERROR]: problem accessing handgun category, " + handgun_url_check[1])

# Checking AR-15/AR-10/AK-47 url
AR_url_check = check_url(categories_array[1])
# AR-15/AR-10/AK-47 url is OK, can continue scraping
if AR_url_check[0]:
    # Getting AR-15/AR-10/AK-47 page html using chromedriver and initializing it as a BeautifulSoup object
    driver.get(categories_array[1])
    AR_page_html = driver.page_source
    AR_page = BeautifulSoup(AR_page_html, 'lxml')
    # Checking to make sure html was properly loaded
    if AR_page is not None:
        # Finding the AR-15/AR-10/AK-47 subcategories and storing them in a list
        print("[INFO]: Locating AR-15/AR-10/AK-47 subcategories...")
        AR_subcategories_menu = AR_page.find(id="catList")
        AR_subcategories_list = AR_subcategories_menu.find_all(class_="item")

        # Isolating and storing in a list links for AR-15/AR-10/AK-47 subcategories, we only want the first one
        AR_subcategories_array = []
        for i in range(1):
            AR_subcategories_array.append(str(AR_subcategories_list[i].find("a", href=True)).split('"')[1])
        print("[INFO]: Located %s/1 AR-15/AR-10/AK-47 subcategories" % len(AR_subcategories_array))

        # Gets all of the links to the AR-15/AR-10/AK-47 listings from the subcategory page
        print("[INFO]: Retrieving all AR-15/AR-10/AK-47 listing links...")
        AR_listings_links = get_listing_links(subcategory_links=AR_subcategories_array)
        print("[INFO]: Found %s AR-15/AR-10/AK-47 listing links" % len(AR_listings_links))

        # Tries to download all of the images associated with AR_listings_links
        print("[INFO]: Downloading AR-15/AR-10/AK-47 listing images...")
        if download_listing_images(listing_links=AR_listings_links, target_dir="D:/TSA-2019-Dataset/AR15_AR10_AK47"):
            print("[INFO]: Successfully downloaded all AR-15/AR-10/AK-47 images")
        else:
            print("[WARNING]: Did not download all AR-15/AR-10/AK-47 images, AR-15/AR-10/AK-47 dataset is incomplete")
    # Html was not loaded properly, next category is scraped
    else:
        print("[ERROR]: problem loading html for AR-15/AR-10/AK-47 category")
# AR-15/AR-10/AK-47 url was not ok, error is printed and next category is scraped
else:
    print("[ERROR]: problem accessing AR-15/AR-10/AK-47 category, " + AR_url_check[1])

# Checking rifle url
rifle_url_check = check_url(categories_array[2])
# Rifle url is OK, can continue scraping
if rifle_url_check[0]:
    # Getting rifle page html using chromedriver and initializing it as a BeautifulSoup object
    driver.get(categories_array[2])
    rifle_page_html = driver.page_source
    rifle_page = BeautifulSoup(rifle_page_html, 'lxml')
    # Chekcing to make sure html was properly loaded
    if rifle_page is not None:
        # Finding the rifle subcategories and storing them in a list
        print("[INFO]: Locating rifle subcategories...")
        rifle_subcategories_menu = rifle_page.find(id="catList")
        rifle_subcategories_list = rifle_subcategories_menu.find_all(class_="item")

        # Isolating and storing in a list links for rifle subcategories, we are interested in all 5
        rifle_subcategories_array = []
        for i in range(5):
            rifle_subcategories_array.append(str(rifle_subcategories_list[i].find("a", href=True)).split('"')[1])
        print("[INFO]: Located %s/5 rifle subcategories" % len(rifle_subcategories_array))

        # Gets all of the links to the rifle listings from the subcategory page
        print("[INFO]: Retrieving all rifle listing links...")
        rifle_listings_links = get_listing_links(subcategory_links=rifle_subcategories_array)
        print("[INFO]: Found %s rifle listing links" % len(rifle_listings_links))

        # Tries to download all of the images associated with rifle_listings_links
        print("[INFO]: Downloading rifle listing images...")
        if download_listing_images(listing_links=rifle_listings_links, target_dir="D:/TSA-2019-Dataset/Rifles"):
            print("[INFO]: Successfully downloaded all rifle images")
        else:
            print("[WARNING]: Did not download all rifle images, rifle dataset is incomplete")
    # Html was not properly loaded, next category is scraped
    else:
        print("[ERROR]: problem loading html for rifle category")
# Rifle url was not ok, error is printed and next category is scraped
else:
    print("[ERROR]: problem accessing rifle category, " + rifle_url_check[1])

# Checking shotgun url
shotgun_url_check = check_url(categories_array[3])
# Shotgun url is OK, can continue scraping
if shotgun_url_check[0]:
    # Getting shotgun page html using chromedriver and initializing it as a BeautifulSoup object
    driver.get(categories_array[3])
    shotgun_page_html = driver.page_source
    shotgun_page = BeautifulSoup(shotgun_page_html, 'lxml')
    # Checking to make sure html was properly loaded
    if shotgun_page is not None:
        # Finding the shotgun subcategories and storing them in a list
        print("[INFO]: Locating shotgun subcategories...")
        shotgun_subcategories_menu = shotgun_page.find(id="catList")
        shotgun_subcategories_list = shotgun_subcategories_menu.find_all(class_="item")

        # Isolating and storing in a list links for shotgun subcategories, we are interested in all 8
        shotgun_subcategories_array = []
        for i in range(8):
            shotgun_subcategories_array.append(str(shotgun_subcategories_list[i].find("a", href=True)).split('"')[1])
        print("[INFO]: Located %s/8 shotgun subcategories" % len(shotgun_subcategories_array))

        # Gets all of the links to the shotgun listings from the subcategory page
        print("[INFO]: Retrieving all shotgun listing links...")
        shotgun_listings_links = get_listing_links(subcategory_links=shotgun_subcategories_array)
        print("[INFO]: Found %s shotgun listing links" % len(shotgun_listings_links))

        # Tries to download all of the images associated with shotgun_listings_links
        print("[INFO]: Downloading shotgun listing images...")
        if download_listing_images(listing_links=shotgun_listings_links, target_dir="D:/TSA-2019-Dataset/Shotguns"):
            print("[INFO]: Successfully downloaded all shotgun images")
        else:
            print("[WARNING]: Did not download all shotgun images, shotgun dataset is incomplete")
    # Html was not properly loaded, next category is scraped
    else:
        print("[ERROR]: problem loading html for shotgun category")
# Shotgun url was not ok, error is printed and next category is scraped
else:
    print("[ERROR]: problem accessing shotgun category, " + shotgun_url_check[1])

# Shutting down chromedriver
driver.close()

# Timing end and conversion from seconds to h:m:s
end = time.time()
total_seconds = end-start
hours = int(total_seconds/3600)
minutes = int((total_seconds - hours*3600)/60)
seconds = int(total_seconds - (hours*3600 + minutes*60))
print("[INFO]: Data collection process took %s:%s:%s (h:m:s)" % (hours, minutes, seconds))
