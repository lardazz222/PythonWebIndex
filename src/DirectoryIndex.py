import requests
import json
from bs4 import BeautifulSoup
from urllib.parse import unquote
import random 
import re

class DirectoryIndex:
    """
    DirectoryIndex class
    Parses Apache DirectoryIndex HTML pages, and returns a list of directories and files.
    """
    
    def __init__(self, url: str):
        self.url = url
        if self.url[-1] == "/":
            self.url = self.url[:-1]
            
        print("URL: " + self.url)
    

    def _get(self, path: str) -> requests.models.Response:
        """
        Get the raw HTML content of the page at the given path.
        <br>
        <b>*Only use on DirectoryIndex pages.*</b>
        ## Parameters
        `path`: `str`
        *Path after base URL, expected to start with "/".*
        """
        response = requests.get(self.url + path)
        
        return response
    
    def get_dir(self, path: str) -> list:
        """
        Return 2 lists (`directories` and `files`) from the provided path.
        """
        html = self._get(path)
        
        resp_type = html.headers["Content-Type"]
        if "text/html" not in resp_type:
            raise Exception("Unexpected content type received: " + resp_type)

        html = html.text
        soup = BeautifulSoup(html, "html.parser")
        dirs = []
        files = []
        for a in soup.find_all("a"):
            href = a.get("href")
            if href == "../":
                continue
            # if ends with /, it's a directory
            if href[-1] == "/":
                dirs.append(unquote(href)[:-1])
            else:
                files.append(unquote(href))
        return dirs,  files
    
    def get_raw(self, path: str) -> bytes:
        """
        Get the raw content of a file in `bytes`.
        """
        data = self._get(path)
        if data.headers["Content-Type"] == "text/html":
            raise Exception("Unexpected content type received: text/html")
        return data.content
    
    def _get_parent_path(self, path: str) -> str:
        """
        Get the parent path of the given path.
        """
        if path == "/":
            return "/"
        if path[-1] == "/":
            path = path[:-1]
        return path[:path.rfind("/")+1]
    
    def stat(self, path: str) -> dict:
        """
        Get the stat of a file. If a path to a directory is given, it will only return the `date`. <br>
        A path to a file returns `date` and `size` (in bytes).
        """
        pass # TODO: Implement stat method. holy fuck its hard :c
            

if __name__ == "__main__": # if being ran as a script
    url = "https://vaporwave.ivan.moe/list/"
    di = DirectoryIndex(url)
    
    
    print("File Stat Test:")
    file = di.stat("/Audi/Audi - finals/11. 1986.wav")
    print(file)