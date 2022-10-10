import requests
from bs4 import BeautifulSoup
import lxml

import json

from fake_useragent import UserAgent
# from random import randrange
ua = UserAgent()
ua_ = ua.random

import time
import re

import openpyxl

excel_file = openpyxl.load_workbook('plz_ort_TEST.xlsx')
employees_sheet = excel_file['Worksheet']
currently_active_sheet = excel_file.active
cell_obj = employees_sheet.cell(row=1, column=1)

headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "User-Agent": f'{ua}'  # "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,
    # like Gecko) Chrome/96.0.4664.45 Safari/537.36"
}

print('start...')

url = 'https://www.barmer-kliniksuche.de/'


client = requests.session()

# Retrieve the CSRF token first
client.get(url)

php__ = client.cookies
php_ = php__['PHPSESSID']

cookies = {
    'PHPSESSID': f'{php_}',
}

all_info = []

for i in range(2, 4):
    plz_ = f'{employees_sheet[f"C{i}"].value}'
    print(f'{plz_} - - - - - - - >>>')
    start_time = time.time()
    # print(f'{employees_sheet[f"C{i}"].value}')
    # fl.writelines(str() + "\n")

    headers = {
        'authority': 'www.barmer-kliniksuche.de',
        'accept': 'application/json, text/javascript, */*; q=0.01',
        'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7,uk;q=0.6,vi;q=0.5,pt;q=0.4,ka;q=0.3',
        # 'cookie': 'PHPSESSID=l2qd8mlv7ral69aoil74kas3bj',
        'referer': 'https://www.barmer-kliniksuche.de/suche/suchergebnis.php?searchdata%5Bplzort%5D=10115&searchdata%5Bmaxdistance%5D=0&searchcontrol%5Border%5D=distance&searchcontrol%5Blimit_offset%5D=50&searchcontrol%5Blimit_num%5D=-48',
        'sec-ch-ua': '"Google Chrome";v="105", "Not)A;Brand";v="8", "Chromium";v="105"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest',
    }

    params = {
        'searchdata[autocomplete]': '',
        'searchdata[plzort]': f'{plz_}',
        'searchdata[location]': '',
        'searchdata[maxdistance]': '0',
        'searchdata[bundesland]': '',
        'searchdata[suchbegriff]': '',
        'searchdata[anzahl_betten_min]': '',
        'searchdata[anzahl_betten_max]': '',
        'searchdata[icd]': '',
        'searchdata[ops]': '',
        'searchdata[eprd]': '',
        'searchcontrol[order]': 'distance',
        'searchcontrol[limit_offset]': '0',
        'searchcontrol[limit_num]': '50',
    }

    response = requests.get('https://www.barmer-kliniksuche.de/api/hospitals', params=params, cookies=cookies, headers=headers)
    # response = requests.get('https://www.barmer-kliniksuche.de/api/autocompletion/locations', params=params,
    #                         cookies=cookies, headers=headers)
    print(response.text)
    aaa = json.loads(response.text)

    plz_info = []

    for i in aaa["data"]:
        id_ = i["id"]
        name_ = i["name"]
        street_ = i["street"]
        zip_ = i["zip"]
        city_ = i["city"]
        federalStateNumber_ = i["federalStateNumber"]
        federalState_ = i["federalState"]
        phone_ = i["phone"]
        email_ = i["email"]
        internet_ = i["internet"]
        lat_ = i["lat"]
        lon_ = i["lon"]
        detailsUrl_ = i["detailsUrl"]

        response = requests.get(url=detailsUrl_, cookies=cookies, headers=headers)
        soup = BeautifulSoup(response.text, 'lxml')
        stand_der_daten = soup.find_all('div', class_='col-sm-6 col-xs-12')
        stand_der_daten__ = stand_der_daten[9].text
        stand_der_daten_ = stand_der_daten__.strip()

        p = re.compile('(uebersicht)')
        url_fachabteilungen = p.sub('fachabteilungen', detailsUrl_)

        response = requests.get(url=url_fachabteilungen, cookies=cookies, headers=headers)
        soup = BeautifulSoup(response.text, 'lxml')
        stand_der_daten = soup.find_all('a', class_='intern')

        fachabteilungen = []
        for i in stand_der_daten:
            url___ = f'https://www.barmer-kliniksuche.de/{i.get("href")}'
            response = requests.get(url=url___, cookies=cookies, headers=headers)
            soup = BeautifulSoup(response.text, 'lxml')
            fachabteilung__ = soup.find('h2', class_='hospital_specialist_department').text
            fachabteilung_ = fachabteilung__.split(': ')[-1]
            arztliche_leitung__ = soup.find('div', class_='col-sm-7 col-xs-12').text
            arztliche_leitung_ = arztliche_leitung__.strip()
            anzahl_vollstationare_falle_ = soup.find('div', class_='col-sm-3 col-xs-12 rowtable-title hyphenate').text

            p = re.compile('(uebersicht)')
            url_ambulante = p.sub('diagnosen-krankheiten-icd', url___)

            response = requests.get(url=url_ambulante, cookies=cookies, headers=headers)
            soup = BeautifulSoup(response.text, 'lxml')
            krankheiten_all = soup.find_all('div', class_='row rowtable-data')

            # len(krankheiten_all)

            # Krankheiten
            krankheiten = []

            for m in krankheiten_all:
                bezeichnung__ = m.find('div', class_='col-sm-4 col-xs-12 rowtable-title hyphenate').text.strip()
                bezeichnung_ = ' '.join(bezeichnung__.split())
                anzahl_ = m.find('div', class_='col-sm-1 col-xs-8 rowtable-title').text.strip()

                krankheiten.append(
                    {
                        "bezeichnung": bezeichnung_,
                        "anzahl": anzahl_
                    }
                )

            # PERSONAL
            personal = []

            p = re.compile('(uebersicht)')
            url_personal = p.sub('personal', url___)
            response = requests.get(url=url_personal, cookies=cookies, headers=headers)
            soup = BeautifulSoup(response.text, 'lxml')
            bezeichnung_all = soup.find_all('div', class_='col-sm-6 col-xs-12 rowtable-title hyphenate')
            anzahl_all = soup.find_all('div', class_='col-sm-2 col-xs-12 rowtable-title hyphenate')

            for index, n in enumerate(bezeichnung_all):
                bezeichnung_ = n.text.strip()
                anzahl_ = anzahl_all[index].text.strip()

                if anzahl_ != '0,00':
                    personal.append(
                        {
                            "bezeichnung": bezeichnung_,
                            "anzahl": anzahl_
                        }
                    )

            fachabteilungen.append(
                {
                    "Fachabteilung": fachabteilung_,
                    "Ärztliche Leitung": arztliche_leitung_,
                    "Anzahl vollstationäre Fälle": anzahl_vollstationare_falle_,
                    "Krankheiten": krankheiten,
                    "Personal": personal
                }
            )

        plz_info.append(
            {
                "name": name_,
                "street": street_,
                "zip": zip_,
                "city": city_,
                "federalStateNumber": federalStateNumber_,
                "federalState": federalState_,
                "phone": phone_,
                "email": email_,
                "internet": internet_,
                "lat": lat_,
                "lon": lon_,
                "detailsUrl": detailsUrl_,
                "standDerDaten": stand_der_daten_,
                "Fachabteilungen": fachabteilungen
            }
        )
    finish_time = time.time() - start_time
    print(f'{finish_time} = = = = = = = = =\n')

    all_info.append(
        {
            "PLZ": plz_,
            "INFO": plz_info
        }
    )

with open(f'___barmer-kliniksuche.de.json', 'w', encoding='utf-8') as file:
    json.dump(all_info, file, indent=4, ensure_ascii=False)
