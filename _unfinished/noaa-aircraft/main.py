
from traffic.data import airports
print(airports['KLAL'].name)
print(airports['KLAL'].latlon)

from traffic.data import opensky
flight = opensky.history(
    "2017-02-05 15:45",
    stop="2017-02-05 16:45",
    callsign="EZY158T",
    # returns a Flight instead of a Traffic
    return_flight=True
)
print(flight)

