import pandas as pd
import numpy as np 
import sqlalchemy
import requests
from datetime import datetime, timedelta
from src import db, create_app
from src.models import *

def delete_table(name):
    name.__table__.drop(db.engine)

def initiate_db(table_name):
    db.create_all()
    print(table_name.query.all())

def get_geolocation(params, ad_id, GOOGLE_MAPS_API_URL = 'https://maps.googleapis.com/maps/api/geocode/json'):
    req = requests.get(GOOGLE_MAPS_API_URL, params=params)

    if req.status_code == 200:
        res = req.json()
        if len(res['results']) > 0:
            result = res['results'][0]

            Googleplace_id = result['place_id']
            #Googleid = result['id']
            #GoogleName = result['name']

            GoogleStreet_Number = ''
            GoogleRoute = ''
            GoogleLocality = ''
            GoogleAdminLevel1 = ''
            GoogleCountry = ''
            GooglePostalCode = ''
            GoogleLatitude = ''
            GoogleLongitude = ''

            for types in result['address_components']:
                field = types.get('types', [])
                if 'street_number' in field:
                    GoogleStreet_Number = types['long_name']
                elif 'route' in field:
                    GoogleRoute = types['long_name']
                elif 'locality' in field:
                    GoogleLocality = types['long_name']
                elif 'administrative_area_level_1' in field:
                    GoogleAdminLevel1 = types['long_name']
                elif 'country' in field:
                    GoogleCountry = types['long_name']
                elif 'postal_code' in field:
                    GooglePostalCode = types['long_name']

            GoogleLatitude = result['geometry']['location']['lat']
            GoogleLongitude = result['geometry']['location']['lng']

            address = Address(civic_number=GoogleStreet_Number,
                            street=GoogleRoute,
                            city=GoogleLocality,
                            state=GoogleAdminLevel1,
                            country=GoogleCountry,
                            postal_code=GooglePostalCode,
                            latitude=GoogleLatitude,
                            longitude=GoogleLongitude,
                            ad_id=ad_id)

            db.session.add(address)
            db.session.commit()
            print("Added to db")


app = create_app()

with app.app_context():
    c = Ad.query.count()
    for i in range(0, c + 1):
        ad = Ad.query.filter_by(ad_id=i).first()
        if ad is None: 
            print("None")
            continue

        address = ad.address
        if address is not None:
            params = {
                'address': address.replace(' ', '+'),
                'key': 'AIzaSyA9u5PnH2nHMiFRWJRWGhtmprCuAueuB2o'
            }

            get_geolocation(params, ad.ad_id)
        else: print(address, 'null')
        

    print(Ad.query.order_by(Ad.ad_id.desc()).first().ad_id)

    print(Ad.query.count())
    a = Address.query.first()
    print(a.latitude, a.longitude)


    # delete_table(Address)
    # initiate_db(Address)

