import requests
from bs4 import BeautifulSoup
import difflib
import time
import urllib.request
from datetime import datetime


def monitor():
    url = "https://nolacoalition.info/"
    
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
    
    PrevVersion = ""
    
    FirstRun = True
    while True:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "lxml")
        
        members = soup.find('div', {'class': 'is-layout-flex wp-container-12 wp-block-columns'})
        # companies = soup.find('div', {'class': 'is-layout-flex wp-container-12 wp-block-columns'})

        soup = members.get_text()
        # print(soup)
        if PrevVersion != soup:
            if FirstRun == True:
                PrevVersion = soup
                FirstRun = False
                print ("Start Monitoring "+url+ ""+ str(datetime.now()))
            else:
                print ("Changes detected at: "+ str(datetime.now()))
                OldPage = PrevVersion.splitlines()
                NewPage = soup.splitlines()
                d = difflib.Differ()
                diff = d.compare(OldPage, NewPage)
                out_text = "\n".join([ll.rstrip() for ll in '\n'.join(diff).splitlines() if ll.strip()])
                print (out_text)
                OldPage = NewPage
                PrevVersion = soup
        else:
            print( "No Changes "+ str(datetime.now()))
        time.sleep(300)
        continue   


if __name__ == "__main__":
    runit = monitor()