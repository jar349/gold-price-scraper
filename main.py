import os

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
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

@app.get("/", response_class=HTMLResponse)
def get_index():
    return """
    <html>
    <head>
    <title>WoW Gold Prices</title>
    </head>
    <body>
      <h2>Recent Gold Prices on Herod - Horde</h2>
      <canvas id="myChart" width="85%" height="85%"></canvas>
      <script src="https://cdnjs.com/libraries/Chart.js"></script>
      <script>
        xhttp.onreadystatechange = function() {
          if (this.readyState == 4 && this.status == 200) {
            const data = this.responseText;
            const renamed_data = data.map(point => ({'t': point['time'],'y': point['price']}))
            var ctx = document.getElementById("myChart")
            var myChart = new Chart(ctx, {
              type: "line",
              data: renamed_data
            })
          }
        };

        xhttp.open("GET", "http://compute.ruiz.house:8088/prices", true);
        xhttp.send();
      </script>
    </body>
    </html>
    """