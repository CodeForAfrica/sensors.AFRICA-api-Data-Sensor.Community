from chalice import Chalice, Rate
from chalicelib import service
from chalicelib.settings import SCHEDULE_RATE

app = Chalice(app_name='sensors-africa-community')

@app.schedule(Rate(int(SCHEDULE_RATE), unit=Rate.MINUTES))
def scheduled(event):
    return service.run()
