import csv
import urllib3
from datetime import datetime
from datetime import date
import time
import json
import threading
import sys
from bs4 import BeautifulSoup

def spinner(stop):
    signs=['\\','|','/','-']
    while True:
        if stop():
            break
        for sign in signs: 
            print(sign,end="\r")
            time.sleep(0.2)

parsing_finished=False
t = threading.Thread(name='loading process', target=spinner, args=(lambda : parsing_finished, ))

#list of data to be written into csv
#children in json represented by '>'
allFiltered=['rank','name','accuracy','play count','pp','ss','s','a','play time','id','join date','playmode','location','interests','twitter','discord']
filters=['>statistics>play_time','id','join_date','playmode','location','interests','twitter','discord']

PAGE_BASE = 'https://osu.ppy.sh/rankings/osu/performance'

if(len(sys.argv)==3):
    COUNTRY=sys.argv[1]
    MAX_PAGE=int(sys.argv[2])
else:
    # Check if user wants to scrape global rankings or country rankings
    print('If you want to scrape the global rankings, enter "global".')
    print('If you want to scrape the rankings of a specific country, enter its country code.')
    print('global/xx')
    COUNTRY = input()

    print('How many pages do you want to scrape?')
    print('One page equals 50 users.')
    MAX_PAGE = int(input())

while MAX_PAGE > 200:
    print('You can only scrape up to 200 pages.')
    MAX_PAGE = int(input())

if COUNTRY == 'global':
    PAGE_BASE = PAGE_BASE + '?page='
else:
    PAGE_BASE = PAGE_BASE + '?country=' + COUNTRY + '&page='

http = urllib3.PoolManager()

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)    

CSV_FILE = 'osu_data_' + COUNTRY + "_" + str(date.today()) + ".csv"

t.start()

for current_row in range(1, MAX_PAGE + 1):
    # Save per page in case something happens
    with open(CSV_FILE, 'a', newline='',encoding='utf-8') as csv_file: 
        writer = csv.writer(csv_file)
        if(current_row==1):
            writer.writerow(allFiltered)
        start = time.time()
        page = http.request('GET', PAGE_BASE + str(current_row))
        parsed_page = BeautifulSoup(page.data, 'html.parser')
        rows = parsed_page.find_all(
            'tr', attrs={'class': 'ranking-page-table__row'})

        for row in rows:
            cols = row.find_all('td', {'class': 'ranking-page-table__column'})
            links = cols[1].find_all('a', href=True)
            #print(links)
            user_profile_link = links[1]['href'].strip()
            user_row = []
            
            for val in cols:
                user_row.append(val.text.strip())    

            profile = http.request('GET', user_profile_link)
            profile_parsed = BeautifulSoup(profile.data, 'html.parser')
            userJsonTag = profile_parsed.find_all("script",{'id':'json-user'})

            #shit solution pls find better
            userString = str(userJsonTag[0]).split('>',1)[1].replace("</script>","")
            userJson = json.loads(userString)
            for item in filters:
                if(item[0]=='>'):
                    entry=item.split('>')
                    user_row.append(userJson[entry[1]][entry[2]])
                else:
                    user_row.append(userJson[item])

            writer.writerow(user_row)
            time.sleep(1)

        time_taken = str(int((time.time() - start) / 60)) + ':' + str(int((time.time() - start) % 60))
        print('processed page',current_row,'time taken:',time_taken)
        page.close()

parsing_finished=True
t.join()
print('finished with parsing {} players from {}'.format(MAX_PAGE*50,COUNTRY))
