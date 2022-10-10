import requests
from bs4 import BeautifulSoup
import lxml

import json

from fake_useragent import UserAgent

# from random import randrange
ua = UserAgent()
ua_ = ua.random

headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "User-Agent": f'{ua}'  # "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,
    # like Gecko) Chrome/96.0.4664.45 Safari/537.36"
}

print('start...')


"""
Need to get a PART1 or PART2 file?
Enter value 1 or 2:
"""

part_ = input('\nNeed to get a PART1 or PART2 file?\nEnter value 1 or 2: ')

if part_ == '1':

    # PART 1 !!!!!!!!!!!!!!!!!!!!!
    #
    url1 = 'https://khstrukturdaten.goeg.at/backend2/KliniksucheV2/api/spitaeler?'

    types_ = ['Gemeinnütziges Krankenhaus', 'Privatkrankenhaus']

    with requests.Session() as session:
        response = session.get(url=url1, headers=headers)

        aaa = json.loads(response.text)

        print(aaa)
        print('--------------')

    hospital_info = []

    cou_ = 0


    for i in aaa:
        cou_ += 1
        nummer = i['nummer']
        print(f'{cou_} ++++++++++++++++++++')
        # nummer = 901
        url2 = f'https://khstrukturdaten.goeg.at/backend2/KliniksucheV2/api/spitaeler/{nummer}'

        with requests.Session() as session:
            response = session.get(url=url2, headers=headers)
            bbb = json.loads(response.text)

            name_ = bbb['name']
            url_ = f"https://kliniksuche.at/klinik/{bbb['nummer']}"

            address_ = f"{bbb['adresse']['strasseHausnummer']} {bbb['adresse']['plzOrt']}"
            tel_ = bbb['kontakt']['telefon']
            fax_ = bbb['kontakt']['fax']
            email_ = bbb['kontakt']['email']
            website_ = bbb['kontakt']['internet']
            # -----------------------------------
            type__ = bbb['typ']
            if type__ == 1:
                type_ = types_[0]
            else:
                type_ = types_[1]
            # -----------------------------------
            lastUpdatedDate_ = bbb['lastUpdatedDate']

            # positions_ = ['Direktion', 'Ärztliche Leitung', 'Pflegedienst-leitung', 'Verwaltungs-leitung', 'Technische Leitung']
            # positions_ = ['direktion', 'aerztlicheLeitung', 'pflegedienstleitung', 'verwaltungsleitung', 'technischeLeitung']

            departments_ = []
            abteilungsleitung_ = []

            for w in bbb['abteilungen']:

                id__ = w['id']
                # id__ = '5d9be90f-7c1d-4019-b0b8-494c3e74a08e'
                print(f'\t{id__}')

                url3 = f'https://khstrukturdaten.goeg.at/backend2/KliniksucheV2/api/spitaeler/901/abteilungen/{id__}'

                with requests.Session() as session:
                    response = session.get(url=url3, headers=headers)
                    ccc = json.loads(response.text)

                # print(f'{cou_}***************************')
                # print(ccc['name'])
                url_ccc = f'https://kliniksuche.at/klinik/901/abteilungen/{id__}'

                abteilungsleitung_.append(
                    {
                        "leitung": ccc['abteilungsleitung']['leitung'],
                        "telefon": ccc['abteilungsleitung']['telefon'],
                        "fax": ccc['abteilungsleitung']['fax'],
                        "email": ccc['abteilungsleitung']['email'],
                        "internet": ccc['abteilungsleitung']['internet']
                    }
                )

                betten_ = ccc['betten']['betten']

                personal_ = []
                for k, v in ccc['personal'].items():
                    personal_.append(
                        {
                            "name": k,
                            "value": v
                        }
                    )

                aktuelleLeistungsschwerpunkte_ = ccc['leistungsschwerpunkte']

                diagnosen_ = []
                for v in ccc['diagnosen']:
                    diagnosen_.append(
                        {
                            "d": v
                        }
                    )

                hospital_info.append(
                    {
                        "name": "Landeskrankenhaus Hartberg",
                        "url": "https://kliniksuche.at/klinik/631",
                        "contactInformation": {
                            "address": address_,
                            "tel": tel_,
                            "fax": fax_,
                            "email": email_,
                            "website": website_,
                            "type": type_,
                            "lastUpdatedDate": lastUpdatedDate_
                        },
                        "managerNames": [
                            {
                                "position": "Direktion",
                                "name": bbb['leitung']['direktion'],
                            },
                            {
                                "position": "Ärztliche Leitung",
                                "name": bbb['leitung']['aerztlicheLeitung'],
                            },
                            {
                                "position": "Pflegedienst-leitung",
                                "name": bbb['leitung']['pflegedienstleitung'],
                            },
                            {
                                "position": "Verwaltungs-leitung",
                                "name": bbb['leitung']['verwaltungsleitung'],
                            },
                            {
                                "position": "Technische Leitung",
                                "name": bbb['leitung']['technischeLeitung']
                            }
                        ],
                        "departments": [
                            {
                                "name": ccc['name'],
                                "url": url_ccc,
                                "abteilungsleitung": abteilungsleitung_

                             }

                        ],
                        "betten": betten_,
                        "personal": personal_,
                        "aktuelleLeistungsschwerpunkte": aktuelleLeistungsschwerpunkte_,
                        "diagnosen": diagnosen_
                    }
                )

    with open(f'___Kliniksuche (Part 1).json', 'w', encoding='utf-8') as file:
        json.dump(hospital_info, file, indent=4, ensure_ascii=False)
    #
    # END of PART 1 ===================================================================================================

elif part_ == '2':

    # PART 2 !!!!!!!!!!!!!!!!!!!!!

    with open('kliniksuche.at_Diagnosen.json', 'r', encoding='utf-8') as set_:
        set_data = json.load(set_)

    """
    !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    requests.exceptions.SSLError – dh key too small
    !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    """

    requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS += 'HIGH:!DH:!aNULL'
    try:
        requests.packages.urllib3.contrib.pyopenssl.DEFAULT_SSL_CIPHER_LIST += 'HIGH:!DH:!aNULL'
    except AttributeError:
        # no pyopenssl support used / needed / available
        pass
    """
    !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    requests.exceptions.SSLError – dh key too small
    !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    """

    dia_arr = []

    for k, v in set_data.items():
        print(f'{k} --->>> {v}')
        url_p2 = f'https://kliniksuche.at/api/hospitals?treatment=20'
        diagnose_ = v
        with requests.Session() as session:
            response = session.get(url=url_p2, headers=headers, verify=False)

        params = {
            'treatment': f'{k}',
        }

        # response = requests.get('https://kliniksuche.at/api/hospitals', params=params, cookies=cookies, headers=headers)

        ppp = json.loads(response.text)

        for h_ in ppp["hospitals"]:
            hospitalName_ = h_["name"]
            cases_ = h_['treatmentCount']
            textToTheRight_ = h_['sites'][0]['treatmentCountHint']

            dia_arr.append(
                {
                    "diagnose": diagnose_,
                    "hospitalName": hospitalName_,
                    "cases": cases_,
                    "textToTheRight": textToTheRight_
                }
            )

    with open(f'___Kliniksuche (Part 2).json', 'w', encoding='utf-8') as file:
        json.dump(dia_arr, file, indent=4, ensure_ascii=False)
    #
    # END of PART 2 ===================================================================================================

else:
    print('=== END ===')
