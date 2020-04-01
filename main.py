import os

from fastapi import FastAPI
from influxdb import InfluxDBClient


app = FastAPI()


@app.get("/prices")
def get_prices(days: int = 7):
    client = InfluxDBClient(
        os.environ.get('INFLUX_HOST', 'influx'),
        os.environ.get('INFLUX_PORT', 8086),
        os.environ.get('INFLUX_USER', 'root'),
        os.environ.get('INFLUX_PASS', 'root'),
        os.environ.get('INFLUX_DB', 'gold-prices')
    )

    result_set = client.query(
        f'SELECT "price" FROM "gold_price" WHERE time >= now() - {days}d'
    )

    return [data_point for data_point in result_set.get_points()]
    