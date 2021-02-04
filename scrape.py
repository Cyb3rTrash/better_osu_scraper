import csv
import urllib3
from datetime import datetime
from datetime import date
import time
import json
from bs4 import BeautifulSoup

#list of data to be written into csv
#children in json representet by '>'
allFiltered=['rank','name','accuracy','play count','pp','ss','s','a','play time','id','join date','playmode','location','interests','skype','twitter','discord']
filters=['>statistics>play_time','id','join_date','playmode','location','interests','skype','twitter','discord']

PAGE_BASE = 'https://osu.ppy.sh/rankings/osu/performance'

# Check if user wants to scrape global rankings or country rankings
print('If you want to scrape the global rankings, enter "global".')
print('If you want to scrape the rankings of a specific country, enter its country code.')
print('global/xx')
COUNTRY = 'DE'

if COUNTRY == 'global':
    PAGE_BASE = PAGE_BASE + '?page='
else:
    PAGE_BASE = PAGE_BASE + '?country=' + COUNTRY + '&page='

print('How many pages do you want to scrape?')
print('One page equals 50 users.')
MAX_PAGE = int(input())
while MAX_PAGE > 200:
    print('You can only scrape up to 200 pages.')
    MAX_PAGE = int(input())

http = urllib3.PoolManager()

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)    

CSV_FILE = 'osu_data_' + COUNTRY + "_" + str(date.today()) + ".csv"

for i in range(1, MAX_PAGE + 1):
    # Save per page in case something happens
    with open(CSV_FILE, 'a', newline='') as csv_file: 
        writer = csv.writer(csv_file)
        if(i==1):
            writer.writerow(allFiltered)
        start = time.time() 
        page = http.request('GET', PAGE_BASE + str(i))
        parsed_page = BeautifulSoup(page.data, 'html.parser')
        rows = parsed_page.find_all(
            'tr', attrs={'class': 'ranking-page-table__row'})

        for row in rows:
            cols = row.find_all('td', {'class': 'ranking-page-table__column'})
            links = cols[1].find_all('a', href=True)
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
        
        print('processed page', i, ' time-taken: ',
              str(int((time.time() - start) / 60)) + ':' + str(int((time.time() - start) % 60)))
        page.close()





