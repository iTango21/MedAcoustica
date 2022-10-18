import requests
from bs4 import BeautifulSoup


# get the list of free proxies
def getproxies():
    r = requests.get('https://free-proxy-list.net/')
    soup = BeautifulSoup(r.content, 'html.parser')
    table = soup.find('tbody')
    proxies = []
    for row in table:
        if (row.find_all('td')[4].text =='elite proxy') & (row.find_all('td')[6].text =='yes'):
            proxy = ':'.join([row.find_all('td')[0].text, row.find_all('td')[1].text])
            proxies.append(proxy)
        else:
            pass
    return proxies

def main():
    pass

if __name__ == '__main__':
    main()