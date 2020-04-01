import datetime
import os
import requests
import time

from influxdb import InfluxDBClient
from lxml import html
from timeloop import Timeloop


tl = Timeloop()


def record_cheapest_price(cheapest_price):
    json_body = [
        {
            "measurement": "gold_price",
            "tags": {
                "server": "Herod",
                "faction": "Horde"
            },
            "time": datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).replace(microsecond=0).isoformat(),
            "fields": {
                "price": f"{cheapest_price:.2f}"  # two decimal places
            }
        }
    ]

    client = InfluxDBClient(
        os.environ.get('INFLUX_HOST', 'influx'),
        os.environ.get('INFLUX_PORT', 8086),
        os.environ.get('INFLUX_USER', 'root'),
        os.environ.get('INFLUX_PASS', 'root'),
        os.environ.get('INFLUX_DB', 'gold-prices')
    )

    # from: https://docs.influxdata.com/influxdb/v1.7/query_language/database_management/#create-database
    # A successful CREATE DATABASE query returns an empty result. If you attempt to create a database that already 
    # exists, InfluxDB does nothing and does not return an error.
    client.create_database(os.environ.get('INFLUX_DB', 'gold-prices'))
    client.write_points(json_body)


@tl.job(interval=datetime.timedelta(hours=6), run_on_start=True)
def scrape_prices():
    page = requests.get('https://www.g2g.com/wow-us/gold-2299-19249?server=30799&faction=543&sorting=price%40asc')
    tree = html.fromstring(page.content)
    all_prices = []
    for price_string in tree.xpath('//span[@class="products__exch-rate"]/span[1]/text()'):
        all_prices.append(float(price_string)*1000)
        
    sorted_prices = sorted(all_prices)
    if len(sorted_prices) == 0:
        return
    
    record_cheapest_price(sorted_prices[0])
    

def main():
    tl.start(block=True)


if __name__ == "__main__":
    main()
