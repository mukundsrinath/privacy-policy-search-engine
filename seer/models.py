from django.db import models

# Create your models here.

class SearchResult:
    def __init__(self, resultid, content="No content found", fileurl="No URL found", text="No text found", html_location="No location found", title="No title found", description="No description found", date="Not Found"): 
        
        self.resultid= resultid
        self.content = content
        self.fileurl = fileurl
        self.text = text
        self.html_location = html_location
        self.title = title
        self.description = description
        self.date = date
