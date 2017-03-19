# TODO: Able for user input of url
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import os
import re
import cssutils
import logging
import argparse


def connection(url):
    """ Connects to a url passed in by argument."""

    print('Connecting to {}'.format(url))
    r = requests.get(url)
    request = r.text
    soup = BeautifulSoup(request, "html.parser")
    return soup.prettify()


def save_html(html):
    """ Save the HTML into a html file called 'index.html'. """

    with open('index.html', 'w') as file:
        file.write(html)


def static_content(html):
    """ Grabbing all link tags and downloading them in the same file structure. """

    global args
    common_css = ['bootstrap', 'font-awesome', 'foundation']
    # css_paths is an empty array that will take all the css paths so a request doesn't need to be made again.
    css_paths = []
    print('Downloading Link Tags')
    soup = BeautifulSoup(html, "html.parser")

    # Main loop that iterates through every <link> tag in html file.
    for link in tqdm(soup.find_all('link')):
        full_path = args.URL + link.get('href')
        r = requests.get(full_path)
        link_text = r.text
        dir_name = re.sub('([a-zA-Z0-9-_.]+\..*)', '', link.get('href'))
        file_name = re.search('([a-zA-Z0-9-_.]+\..*)', link.get('href')).group(1)
        # Checks to see if it's a cdn. If not then create directory.
        if 'http' not in dir_name:
            if not os.path.exists(dir_name):
                os.makedirs(dir_name)
            with open(dir_name + file_name, 'w') as file:
                css_paths.append(dir_name + file_name)
                file.write(link_text)

    print('Downloading Images...')
    for tag in tqdm(soup.find_all('img')):
        full_path = args.URL + tag.get('src')
        r = requests.get(full_path)
        link_content = r.content
        dir_name = re.sub('([a-zA-Z0-9-_.]+\..*)', '', tag.get('src'))
        file_name = re.search('([a-zA-Z0-9-_.]+\..*)', tag.get('src')).group(1)
        # Checks to see if it's a cdn. If it isn't check to see if directory is created then save file.
        if 'http' not in dir_name:
            if not os.path.exists(dir_name):
                os.makedirs(dir_name)
            with open(dir_name + file_name, 'wb') as file:
                file.write(link_content)

    print('Downloading script files')
    for link in tqdm(soup.find_all('script')):
        full_path = args.URL + link.get('src')
        r = requests.get(full_path)
        link_text = r.text
        dir_name = re.sub('([a-zA-Z0-9-_.]+\..*)', '', link.get('src'))
        file_name = re.search('([a-zA-Z0-9-_.]+\..*)', link.get('src')).group(1)

        # Checks to see if it's a cdn. If not then create directory.
        if 'http' not in dir_name:
            if not os.path.exists(dir_name):
                os.makedirs(dir_name)
            with open(dir_name + file_name, 'w') as file:
                file.write(link_text)

    print('Downloading images from CSS files')
    # stops cssutils from printing off Warnings and Errors.
    cssutils.log.setLevel(logging.CRITICAL)
    background_images = []

    # Grab CSS paths and make them a string to easily download
    for path in css_paths:
        if path not in common_css:
            with open(path, 'r') as css_content:
                css = css_content.read()
            sheet = cssutils.parseString(css)

            for rule in sheet:
                if rule.type == rule.STYLE_RULE:
                    for property in rule.style:
                        if property.name == 'background':
                            if 'url' in property.value:
                                value = property.value[4:]
                                parsed_value = value.partition(')')[0]
                                # if there is ../ in string remove it.
                                if '../' in property.value:
                                    value = property.value[7:]
                                    parsed_value = value.partition(')')[0]
                                background_images.append(parsed_value)
                            else:
                                pass
                        else:
                            pass
    print('Downloading extra images')
    for image in tqdm(background_images):
        full_path = args.URL + image
        r = requests.get(full_path)
        link_content = r.content
        dir_name = re.sub('([a-zA-Z0-9-_.]+\..*)', '', image)
        file_name = re.search('([a-zA-Z0-9-_.]+\..*)', image).group(1)
        # Checks to see if it's a cdn. If it isn't check to see if directory is created then save file.
        if 'http' not in dir_name:
            if not os.path.exists(dir_name):
                os.makedirs(dir_name)
            with open(dir_name + file_name, 'wb') as file:
                file.write(link_content)


# What gets executed
parser = argparse.ArgumentParser(description='Insert a URL')
parser.add_argument('URL', metavar='URL', type=str, help="Insert a URL to download.")
args = parser.parse_args()
html_code = connection(args.URL)
save_html(html_code)
static_content(html_code)
