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
        if path[-1] == "/":
            path = path[:-1] # prevent possible path error
        data = self._get(path)
        date = ""
        
        size = 0
        parent_path = ""
        isFile = False
        file_name = path.split("/")[-1]
        if data.headers['Content-Type'] != "text/html": # not a dir
            # get the parent path
            isFile = True
            size = int(data.headers["Content-Length"])
            parent_path = self._get_parent_path(path)
            data = self._get(parent_path)
        else:
            # file_name will be the directory name, without the parenting paths
            file_name = path.split("/")[-1]
            if file_name[-1] == "/":
                file_name = file_name[:-1]
            
        # We need to write a custom parser to get the date. It is present in in the request body HTML, however it is not formatted in a way that can be easily parsed.
        # Example: <a href="...">...</a>  2021-08-01 12:00 // and so on
        # seperate the date from the rest of the text
        sp = BeautifulSoup(data.text, "html.parser")
        
        # get the <pre> element
        pre = sp.find("pre")
        
        # remove each <a> element
        index_map = {}
        i = 0
        for a in pre.find_all("a"):
            index_map[i] = unquote( a.attrs["href"])
            i += 1
            a.decompose()
            
        # get the text
        text = pre.get_text()
        
        # split the text by newline
        k = text.split("\n")
        pattern = re.compile(r'(\d{2}-\w{3}-\d{4} \d{2}:\d{2})\s+(\d+)')
        lines =  [
            (match.group(1), int(match.group(2)))
            for line in k
            if (match := pattern.search(line))
        ]
        # match the index of the provided path with the lines array
        for obj in lines:
            if file_name in index_map.values():
                date = obj[0]
                break
            
        if isFile:
            return {"date": date, "size": size}
        else:
            return {"date": date}
    
if __name__ == "__main__": # if being ran as a script
    url = "https://vaporwave.ivan.moe/list/"
    di = DirectoryIndex(url)
    
    
    print("File Stat Test:")
    file = di.stat("/B o d y l i n e/B o d y l i n e - LIGHT DESIGN")
    print(file)