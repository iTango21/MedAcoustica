import requests
import json

import logging

from scrapeproxies import getproxies
from fake_useragent import UserAgent

ua = UserAgent()
ua_ = ua.random

headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "User-Agent": f'{ua}'
}

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [%(levelname)s] - %(app)s - %(name)s - (%(filename)s).%(funcName)s(%(lineno)d) - %(message)s",
    filename=f'debug_kliniksuche.at.log'
)

logger = logging.getLogger(__name__)
logger = logging.LoggerAdapter(logger, {"app": "kliniksuche.at"})
logger.info("Start programm...")

proxylist = []
proxy = []


def get_proxy():
    global proxylist, proxy

    proxylist = getproxies()
    logger.info(f'Found: {len(proxylist)} proxys.')
    proxy = proxylist[0]

get_proxy()

def chek_proxy(p__):
    global proxy

    tr_ = False
    try:
        requests.get('https://httpbin.org/ip', headers=headers, proxies={'http': p__, 'https': p__}, timeout=2)
        tr_ = True
    except:
        pass

    if tr_:
        pass
    else:
        logger.info('PROXY ERROR!!!')
        get_proxy()
        for i, p_ in enumerate(proxylist):
            try:
                r = requests.get('https://httpbin.org/ip', headers=headers, proxies={'http': p_, 'https': p_},
                                 timeout=2)
                logger.info(f'{i} PROXY: {p_} --->>> success! there is access...')
                proxy = p_
                break
            except:
                logger.info(f'{i} PROXY: {p_} --->>> timeout expired!')

# PART 1
#
url1 = 'https://khstrukturdaten.goeg.at/backend2/KliniksucheV2/api/spitaeler?'

types_ = ['Gemeinnütziges Krankenhaus', 'Privatkrankenhaus']

with requests.Session() as session:
    chek_proxy(proxy)
    response = session.get(url=url1, headers=headers, proxies={'http': proxy, 'https': proxy})

    aaa = json.loads(response.text)

    logger.info(f'In {url1}\nFOUND: {len(aaa)} hospitals')

hospital_info = []
cou_ = 0

for i in aaa:
    cou_ += 1
    nummer = i['nummer']
    print(f'{cou_} ++++++++++++++++++++')
    logger.info(f'{cou_} ++++++++++++++++++++')

    url2 = f'https://khstrukturdaten.goeg.at/backend2/KliniksucheV2/api/spitaeler/{nummer}'

    with requests.Session() as session:
        chek_proxy(proxy)
        response = session.get(url=url2, headers=headers, proxies={'http': proxy, 'https': proxy})
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

        departments_ = []
        abteilungsleitung_ = []

        logger.info(f"{url2} --->>> SUCCESS")

        for w in bbb['abteilungen']:

            id__ = w['id']

            url3 = f'https://khstrukturdaten.goeg.at/backend2/KliniksucheV2/api/spitaeler/901/abteilungen/{id__}'

            with requests.Session() as session:
                chek_proxy(proxy)
                response = session.get(url=url3, headers=headers, proxies={'http': proxy, 'https': proxy})
                ccc = json.loads(response.text)

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

            logger.info(f"{id__} --->>> OK!")

with open(f'kliniksuchePart_1.json', 'w', encoding='utf-8') as file:
    json.dump(hospital_info, file, indent=4, ensure_ascii=False)

logger.info(f"FILE: kliniksuchePart_1.json saved successfully!\n\n")
#
# END of PART 1 ===================================================================================================
#
# PART 2
#
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

logger.info(f" = = = = = Diagnosen = = = = =\n\n")

for k, v in set_data.items():
    url_p2 = f'https://kliniksuche.at/api/hospitals?treatment=20'
    diagnose_ = v

    with requests.Session() as session:
        chek_proxy(proxy)
        response = session.get(url=url_p2, headers=headers, verify=False, proxies={'http': proxy, 'https': proxy})

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
    logger.info(f"{k} --->>> {v} --->>> SUCCESS")

with open(f'___Kliniksuche (Part 2).json', 'w', encoding='utf-8') as file:
    json.dump(dia_arr, file, indent=4, ensure_ascii=False)

logger.info(f"FILE: kliniksuchePart_2.json saved successfully!\n\n")
logger.info('Data collection SUCCESSFULLY completed!')
#
# END of PART 2 ===================================================================================================


def main():
    pass


if __name__ == '__main__':
    main()
