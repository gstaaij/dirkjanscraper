#!/usr/bin/env python3

import urllib.request as request
from html.parser import HTMLParser
import shutil
import os

BASE_PATH = "dirkjan"

class DirkjanHTMLParser(HTMLParser):
    def __init__(self, shouldBranchOut: bool = False, initialUrl: str = ""):
        super().__init__()
        self.shouldBranchOut: bool = shouldBranchOut
        self.initialUrl: str = initialUrl
        self.shouldGetCurrentImageURL: bool = False
        self.urls: [str] = []
        self.currentImageURL: str = ""

    def handle_starttag(self, tag, attrs):
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
        if (tag == "article"):
            for attr in attrs:
                if (attr[0] == "class" and "cartoon" in attr[1].split(" ")):
                    self.shouldGetCurrentImageURL = True
                    break

    def handle_startendtag(self, tag, attrs):
        if (self.shouldGetCurrentImageURL and tag == "img"):
            for attr in attrs:
                if (attr[0] == "src"):
                    self.currentImageURL = attr[1]
                    self.shouldGetCurrentImageURL = False
                    break
    
    def handle_endtag(self, tag):
        if (self.shouldGetCurrentImageURL and tag == "article"):
            self.shouldGetCurrentImageURL = False
    
    def download_images(self):
        if (self.shouldBranchOut):
            for url in self.urls:
                with request.urlopen(url) as response:
                    dhtmlparser = DirkjanHTMLParser(False, url)
                    dhtmlparser.feed(str(response.read()))
                    dhtmlparser.download_images()
        else:
            initialUrlSplit = self.initialUrl.split("/")
            path = ""
            year = ""
            month = ""
            day = ""
            for urlPart in initialUrlSplit:
                try:
                    if (len(urlPart) > 0 and int(urlPart[0]) >= 2):
                        year = urlPart[:4]
                        month = urlPart[4:6]
                        day = urlPart[6:8]
                except ValueError as e:
                    pass
            if (year == ""):
                print(f"Something went wrong trying to download {self.initialUrl}")
                return
            path = BASE_PATH + f"/{year}/{month}"
            os.makedirs(path, exist_ok=True)
            extension = self.currentImageURL.split("/")[-1].split(".")[-1]
            path += f"/dirkjan_{year}{month}{day}.{extension}"
            if (os.path.exists(path)):
                print(f"{path} exists. Skipping...")
                return
            print(path)
            with request.urlopen(self.currentImageURL) as response:
                with open(path, "wb") as file:
                    shutil.copyfileobj(response, file)

def main():
    with request.urlopen("https://dirkjan.nl/cartoon") as response:
        dhtmlparser = DirkjanHTMLParser(True)
        dhtmlparser.feed(str(response.read()))
        dhtmlparser.download_images()

if __name__ == "__main__":
    main()
