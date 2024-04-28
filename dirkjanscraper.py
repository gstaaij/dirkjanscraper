#!/usr/bin/env python3

import urllib.request as request
from html.parser import HTMLParser
import shutil
import os

BASE_PATH = "dirkjan"

class DirkjanHTMLParser(HTMLParser):
    def __init__(self, shouldBranchOut: bool = False, initialUrl: str = ""):
        super().__init__()
        # Whether this object should recursively create more objects to download the cartoons of all URLs for this week
        self.shouldBranchOut: bool = shouldBranchOut
        # The "parent" URL. This is used for giving a name to the downloaded file
        self.initialUrl: str = initialUrl
        # Whether we're currently in an `article` tag with the `cartoon` class.
        # This is used to get the image that should be downloaded
        self.shouldGetCurrentImageURL: bool = False
        # The links to all of the cartoons for this week
        self.urls: [str] = []
        # The URL of the image that is displayed on this page
        self.currentImageURL: str = ""

    def handle_starttag(self, tag, attrs):
        # If it's an `a` tag and it has the class `post-navigation__day` this is a link to
        # another day of the week and we should add it to the list of URLs
        if (self.shouldBranchOut and tag == "a"):
            href: str
            isCartoonLink = False
            for attr in attrs:
                if (attr[0] == "href"):
                    href = attr[1]
                if (attr[0] == "class" and "post-navigation__day" in attr[1].split(" ")):
                    isCartoonLink = True
            if (isCartoonLink):
                self.urls.append(href)
        # If it's an `article` tag and it has the class `cartoon`, this is the element where the cartoon image resides
        if (tag == "article"):
            for attr in attrs:
                if (attr[0] == "class" and "cartoon" in attr[1].split(" ")):
                    self.shouldGetCurrentImageURL = True
                    break

    def handle_startendtag(self, tag, attrs):
        # If it's an `img` tag within the `article` tag mentioned above, this is the cartoon image for this day
        if (self.shouldGetCurrentImageURL and tag == "img"):
            for attr in attrs:
                if (attr[0] == "src"):
                    self.currentImageURL = attr[1]
                    self.shouldGetCurrentImageURL = False
                    break
    
    def handle_endtag(self, tag):
        # If the `article` tag closes, we should no longer look for `img` tags
        if (self.shouldGetCurrentImageURL and tag == "article"):
            self.shouldGetCurrentImageURL = False
    
    def download_images(self):
        if (self.shouldBranchOut):
            # Traverse all the days of the week if needed
            for url in self.urls:
                # Open the URL and run the HTML parser without recursion this time
                with request.urlopen(url) as response:
                    dhtmlparser = DirkjanHTMLParser(False, url)
                    dhtmlparser.feed(str(response.read()))
                    dhtmlparser.download_images()
        elif (self.currentImageURL == ""):
            # If the currentImageURL isn't populated, we can't continue and something is seriously wrong
            print(f"!!! ERROR: couldn't find cartoon on page {self.initalUrl} !!!")
            return
        else:
            # The parent URL split at the slashes
            initialUrlSplit = self.initialUrl.split("/")
            path = ""
            year = ""
            month = ""
            day = ""
            # Go through every part of the parent URL to find the date
            for urlPart in initialUrlSplit:
                try:
                    if (len(urlPart) >= 8 and int(urlPart[0]) >= 2):
                        year = urlPart[:4]
                        month = urlPart[4:6]
                        day = urlPart[6:8]
                except ValueError as e:
                    pass
            if (year == ""):
                print(f"!!! ERROR: Couldn't find the date of {self.initialUrl} !!!")
                return
            
            path = BASE_PATH + f"/{year}/{month}"
            # Make the directory if it doesn't exist already
            os.makedirs(path, exist_ok=True)

            extension = self.currentImageURL.split("/")[-1].split(".")[-1]
            # Add the file name to the path
            path += f"/dirkjan_{year}{month}{day}.{extension}"
            # If the file already exists, skip it
            if (os.path.exists(path)):
                print(f"{path} exists. Skipping...")
                return
            
            # Log the file being downloaded
            print(path)
            
            # Download the file
            with request.urlopen(self.currentImageURL) as response:
                with open(path, "wb") as file:
                    shutil.copyfileobj(response, file)

def main():
    # Open the URL and run the HTML parser with recursion
    with request.urlopen("https://dirkjan.nl/cartoon") as response:
        dhtmlparser = DirkjanHTMLParser(True)
        dhtmlparser.feed(str(response.read()))
        dhtmlparser.download_images()

if __name__ == "__main__":
    main()
