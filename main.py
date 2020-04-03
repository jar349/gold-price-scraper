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
      <script src="https://cdnjs.cloudflare.com/ajax/libs/moment.js/2.24.0/moment.min.js"></script>
      <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/2.9.3/Chart.min.js"></script>
      <script>
        var timeFormat = 'MM/DD HH:mm';
        var xhttp = new XMLHttpRequest();
        xhttp.onreadystatechange = function() {
          if (this.readyState == 4 && this.status == 200) {
            const datapoints = Array.from(xhttp.responseText);
            var ctx = document.getElementById("myChart").getContext('2d');
            var myChart = new Chart(ctx, {
              type: "line",
              data: {
                labels: datapoints.map(point => moment(point['time'])),
                datasets: [{
                    fill: false,
                    backgroundColor: "#FF4136",
					borderColor: "#FF4136",
                    label: "USD Per 1000g",
                    lineTension: 0,
                    data: datapoints.map(point => point['price'])
                }]
              },
              options: {
                fill: false,
                responsive: true,
                scales: {
                  yAxes: [{
                    ticks: {
                      beginAtZero: true
                    },
                    display: true,
                    scaleLabel: {
                      display: true,
                      labelString: "US Dollars"
                    }
                  }],
                  xAxes: [{
                    type: "time",
                    display: true,
                    scaleLabel: {
                        display: true,
                        labelString: "Date"
                    }
                  }]
                }
              }
            })
          }
        };

        xhttp.open("GET", "/prices", true);
        xhttp.send();
      </script>
    </body>
    </html>
    """