from pathlib import Path
import requests, json
import numpy as np


flight_numbers = np.loadtxt('./flight-numbers-flightradar24.txt', dtype=str)
for flight_number in flight_numbers:
    existing_data = [x.name for x in Path('./data-flightradar24').glob('*.json')]
    if flight_number + '.json' not in existing_data:
        complete_fraction = str(len(existing_data) + 1).zfill(4) + ' / ' + str(len(flight_numbers))
        complete_percent = '(' + str(format(100 * len(existing_data) / len(flight_numbers), '.2f')) + '%)'
        print(complete_fraction, complete_percent, '---', flight_number)
        url = 'https://api.flightradar24.com/common/v1/flight-playback.json?flightId={}'.format(flight_number)
        response = requests.get(url, headers={
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:147.0) Gecko/20100101 Firefox/147.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Priority": "u=0, i"
        })
        data = response.json()
        with open('./data-flightradar24/{}.json'.format(flight_number), 'w') as f:
            json.dump(data, f, indent=4)

# can check file:
# e.g., https://www.flightradar24.com/download/?flight=3bcf34da&file=csv
# e.g., https://www.flightradar24.com/data/aircraft/n57rf#40234dee
