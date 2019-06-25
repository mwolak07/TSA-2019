import requests
import io
import os
import validators
from bs4 import BeautifulSoup
import time


# Uses requests to download an image as a jpg
# Saves image to specified directory with specified name
# If specified directory does not exist, it is created.
# Returns true if:
#   - image is saved successfully
# Returns false if:
#   - request did not return ok http status code
#   - content is not an image
#   - url doesn't exist
def download_jpg(image_url, image_name, image_dir, **kwargs):
    # Checks to see if image_dir exits, creates it if it does not
    if not os.path.isdir(image_dir):
        os.mkdir(image_dir)

    # Ensures url is valid
    if not validators.url(image_url):
        return False

    image = requests.get(image_url)  # getting image w/ requests
    full_path = image_dir + "/" + image_name + ".jpg"  # Setting the full path and adding .jpg extension

    # Makes sure image request was ok (http status check) and image request data type is actually an image
    if image.ok and "image" in image.headers['Content-Type']:
        # Uses io.open to save image acquired by requests as a file
        with io.open(full_path, 'wb') as file:
            file.write(image.content)
        return True
    else:
        return False


# Goes through subcategory pages, getting the links for every individual gun listing
# First iterates through all of the subcategories
# For each subcategory, iterates through every product page in the subcategory,
# using the next button to load the next product page
#   - Stops when next_button is not found, indicating the last product page was found
# For each product page, finds the listings and isolates the links to the listing pages,
# adding those links to the gun_listing_links array
# When all of this is finished, gun_listing_links array is returned
# 1st array element indicates if operation was successful
# 1st element will be True if:
#   - All calls to get_site were successful, meaning no pages were invalid
# 1st element will be False if:
#   - All calls to get_site were not successful, meaning not all pages were valid
# If the 1st element if "F", the links may still be usable, though incomplete.
# This is because any invalid links are automatically thrown out
def get_listing_links(subcategory_links, **kwargs):
    gun_listing_links = []
    # Iterates through every subcategory page
    for link in subcategory_links:
        subcategory_page_request = requests.get(link)
        subcategory_page = BeautifulSoup(subcategory_page_request.content, 'lxml')

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
            next_page_request = requests.get(next_page_link)
            next_page = BeautifulSoup(next_page_request.content, 'lxml')
            gun_listing_menu = next_page.find(class_="products-grid products-grid--max-4-col")
            gun_listing_list = gun_listing_menu.find_all(class_="item")
            # Isolating links for gun listings, storing them in gun_listing_links array
            for gun_listing in gun_listing_list:
                gun_listing_links.append(str(gun_listing.find("a", href=True)).split('"')[3])
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
        listing_page_request = requests.get(listing_links[link_number])
        listing_page = BeautifulSoup(listing_page_request.content, 'lxml')
        # Locating link to image
        image_link = str(listing_page.find(id="image-main")).split('src')[1].split('"')[1]
        if not download_jpg(image_url=image_link, image_name=str(link_number), image_dir=target_dir):
            success = False
    return success


# Timing start
start = time.time()

# Getting main page using requests and initializing it as a BeautifulSoup object
main_page_request = requests.get("https://grabagun.com/firearms.html")
main_page = BeautifulSoup(main_page_request.content, 'lxml')

# Finding the individual gun categories and storing them in a list
print("Locating gun categories...")
categories_menu = main_page.find(id="catList")
categories_list = categories_menu.find_all(class_="item")

# Isolating href link of each category and storing this information in an array
# We are only looking for the first 4 categories, as the last 4 are irrelevant to us
categories_array = []
for i in range(4):
    categories_array.append(str(categories_list[i].find("a", href=True)).split('"')[1])
print("Located %s/4 gun categories\n" % len(categories_array))

# Getting handgun page using requests and initializing it as a BeautifulSoup object
handgun_page_request = requests.get(categories_array[0])
handgun_page = BeautifulSoup(handgun_page_request.content, 'lxml')

# Finding the handgun subcategories and storing them in a list
print("Locating handgun subcategories...")
handgun_subcategories_menu = handgun_page.find(id="catList")
handgun_subcategories_list = handgun_subcategories_menu.find_all(class_="item")

# Isolating and storing in a list links for handgun subcategories, we are only interested in the first 3
handgun_subcategories_array = []
for i in range(3):
    handgun_subcategories_array.append(str(handgun_subcategories_list[i].find("a", href=True)).split('"')[1])
print("Located %s/3 handgun subcategories\n" % len(handgun_subcategories_array))

# Gets all of the links to the handgun listings from the subcategory page
print("Retrieving all handgun listing links...")
handgun_listings_links = get_listing_links(subcategory_links=handgun_subcategories_array)
print("Found %s handgun listing links\n" % len(handgun_listings_links))

# Tries to download all of the images associated with handgun_listings_links
print("Downloading handgun listing images...")
if download_listing_images(listing_links=handgun_listings_links, target_dir="D:/TSA-2019-Dataset/Handguns"):
    print("Successfully downloaded all handgun images\n")
else:
    print("Did not download all handgun images, handgun dataset is incomplete\n")

# Getting AR-15/AR-10/AK-47 page using requests and initializing it as a BeautifulSoup object
AR_page_request = requests.get(categories_array[1])
AR_page = BeautifulSoup(AR_page_request.content, 'lxml')

# Finding the AR-15/AR-10/AK-47 subcategories and storing them in a list
print("Locating AR-15/AR-10/AK-47 subcategories...")
AR_subcategories_menu = AR_page.find(id="catList")
AR_subcategories_list = AR_subcategories_menu.find_all(class_="item")

# Isolating and storing in a list links for AR-15/AR-10/AK-47 subcategories, we are only interested in the first 1
AR_subcategories_array = []
for i in range(1):
    AR_subcategories_array.append(str(AR_subcategories_list[i].find("a", href=True)).split('"')[1])
print("Located %s/1 AR-15/AR-10/AK-47 subcategories\n" % len(AR_subcategories_array))

# Gets all of the links to the AR-15/AR-10/AK-47 listings from the subcategory page
print("Retrieving all AR-15/AR-10/AK-47 listing links...")
AR_listings_links = get_listing_links(subcategory_links=AR_subcategories_array)
print("Found %s AR-15/AR-10/AK-47 listing links\n" % len(AR_listings_links))

# Tries to download all of the images associated with AR_listings_links
print("Downloading AR-15/AR-10/AK-47 listing images...")
if download_listing_images(listing_links=AR_listings_links, target_dir="D:/TSA-2019-Dataset/AR15_AR10_AK47"):
    print("Successfully downloaded all AR-15/AR-10/AK-47 images\n")
else:
    print("Did not download all AR-15/AR-10/AK-47 images, AR-15/AR-10/AK-47 dataset is incomplete\n")

# Getting rifle page using requests and initializing it as a BeautifulSoup object
rifle_page_request = requests.get(categories_array[2])
rifle_page = BeautifulSoup(rifle_page_request.content, 'lxml')

# Finding the rifle subcategories and storing them in a list
print("Locating rifle subcategories...")
rifle_subcategories_menu = rifle_page.find(id="catList")
rifle_subcategories_list = rifle_subcategories_menu.find_all(class_="item")

# Isolating and storing in a list links for rifle subcategories, we are interested in all 5
rifle_subcategories_array = []
for i in range(5):
    rifle_subcategories_array.append(str(rifle_subcategories_list[i].find("a", href=True)).split('"')[1])
print("Located %s/5 rifle subcategories\n" % len(rifle_subcategories_array))

# Gets all of the links to the rifle listings from the subcategory page
print("Retrieving all rifle listing links...")
rifle_listings_links = get_listing_links(subcategory_links=rifle_subcategories_array)
print("Found %s rifle listing links\n" % len(rifle_listings_links))

# Tries to download all of the images associated with rifle_listings_links
print("Downloading rifle listing images...")
if download_listing_images(listing_links=rifle_listings_links, target_dir="D:/TSA-2019-Dataset/Rifles"):
    print("Successfully downloaded all rifle images\n")
else:
    print("Did not download all rifle images, rifle dataset is incomplete\n")

# Getting shotgun page using requests and initializing it as a BeautifulSoup object
shotgun_page_request = requests.get(categories_array[3])
shotgun_page = BeautifulSoup(shotgun_page_request.content, 'lxml')

# Finding the shotgun subcategories and storing them in a list
print("Locating shotgun subcategories...")
shotgun_subcategories_menu = shotgun_page.find(id="catList")
shotgun_subcategories_list = shotgun_subcategories_menu.find_all(class_="item")

# Isolating and storing in a list links for shotgun subcategories, we are interested in all 8
shotgun_subcategories_array = []
for i in range(8):
    shotgun_subcategories_array.append(str(shotgun_subcategories_list[i].find("a", href=True)).split('"')[1])
print("Located %s/8 shotgun subcategories\n" % len(shotgun_subcategories_array))

# Gets all of the links to the shotgun listings from the subcategory page
print("Retrieving all shotgun listing links...")
shotgun_listings_links = get_listing_links(subcategory_links=shotgun_subcategories_array)
print("Found %s shotgun listing links\n" % len(shotgun_listings_links))

# Tries to download all of the images associated with shotgun_listings_links
print("Downloading shotgun listing images...")
if download_listing_images(listing_links=shotgun_listings_links, target_dir="D:/TSA-2019-Dataset/Shotguns"):
    print("Successfully downloaded all shotgun images\n")
else:
    print("Did not download all shotgun images, shotgun dataset is incomplete\n")

# Timing end and conversion from seconds to h:m:s
end = time.time()
total_seconds = end-start
hours = int(total_seconds/3600)
minutes = int((total_seconds - hours*3600)/60)
seconds = int(total_seconds - (hours*3600 + minutes*60))
print("Data collection process took %s:%s:%s (h:m:s)" % (hours, minutes, seconds))
