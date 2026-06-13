from pathlib import Path
from datetime import datetime


year = 2024

flight_numbers = []
existing_data = [x.name for x in Path('./data-flightradar24').rglob('*.json')]
webpages = Path('./webpages-flightradar24').glob('*.html')
for path in webpages:
    tail_number = str(path).split('/')[-1].split(' ')[0]
    print(tail_number, len(flight_numbers))
    with open(path, 'r') as f:
        html = f.read()
        for x in html.split('data-flight="'):
            flight_number = x.split('" data-timestamp="')[0]
            timestamp = int(x.split('" data-timestamp="')[1].split('">')[0])
            data_year = datetime.fromtimestamp(timestamp).year
            if (len(flight_number) == 8) and (data_year == year):
                if not '{}.json'.format(flight_number) in existing_data:
                    flight_numbers.append(flight_number)
unique_flight_numbers = list(set(flight_numbers))
with open('flight-numbers-flightradar24.txt', 'w') as o:
    o.write('\n'.join(unique_flight_numbers))
print('wrote {} flight numbers'.format(len(unique_flight_numbers)))
