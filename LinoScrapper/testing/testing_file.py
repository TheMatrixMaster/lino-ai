import glob
import json

import requests


# Numpy Array to JSON
url = "https://www.kijiji.ca/v-apartments-condos/laval-rive-nord/4-1-2-2-ch-2-bdrm-a-louer-a-boisbriand/1448058430"

data = {"ad_url": url, "key": None, "delay": None, "no_images": False}

# Call to API pour envoyer une numpy image en json
r = requests.post('http://127.0.0.1:5000/ads/extract', json=data)
print(r.status_code)
print(r.text)