# -*- coding: utf-8 -*-
# @Author: stephen.zlu
# @Date:   2019-09-10 20:58:26
# @Last Modified by:   slu13
# @Last Modified time: 2019-09-26 22:53:43

from flask import url_for
import requests
import numpy as np
import json
import math
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def fake_webscraper():

    header_info = {
        'title': 'GRIFFINTOWN - Condo 3-1 / 2 - Furnished-Deck 1 Sep 2019',
        'rental_price': '16strides,00 $',
        'Rooms': "3 1/2",
        'address': "315 Rue Richmond, Montréal, QC H3J 1S1, Canada"
    }

    general_info = {
        'Housing type': "Condo",
        'Bathrooms': "1",
        'Services': 'water',
        'Parking': '1',
        'Lease term': "1 year",
        'Moving date': 'August 31, 2019'
    }

    housing_info = {
        'Size': "632 square feet",
        'Furniture': "yes",
        'Appliances': "None",
        'Air conditioning': "yes",
        'Private outdoor areas': ['garden', 'balcony']
    }

    building_info = {
        'Amenities in the building': ['Elevator']
    }

    description =   """
                    Griffintown West - Bass Phase I. New condominium on the ground floor. The condo includes 1 bedroom and 1 full bathroom. Exceptional brightness thanks to its abundant floor-ceiling windows in front. 632 ft. Living space because. + large terrace of 240 ft. because. + 1 storage in the basement. Gym / balcony / pool / roof terrace. Live the Lachine Canal fully. $ 16strides unfurnished, $ 1700 furnished, Indoor parking $ 175 (nego) INCLUDED: + Access to the gym, communal terrace and rooftop pool. + Abundant brightness with 9 feet ceiling + fitted kitchen (stove, fridge, dishwasher and hood) + washer and dryer, light fixtures, curtains and wall mounted air conditioner + master bedroom: 12 '' x 9 '+ large terrace 20 'x 12' (240 ft2) Belted Concrete

                    Excluded: Electricity and internet

                    Close to all amenities: Bixi station at the foot of the building, close to the Lachine Canal, restaurants, bakeries, pharmacies, cafes and others. 15 minutes walk from Georges-Vanier metro, Lucien Lallier train station (Bell Center) and ÉTS.

                    PLEASE NOTE: a) No pets (allowed cat) b) Non-smoking apartment c) f) The tenant must comply with the rules of the building which no short-term sublet such as Airbnb. Please sent me a message if you want a description in English.
                    """

    return header_info, general_info, housing_info, building_info, description


def create_graph_data(data):

    graph_data = {}

    strides = int((max(data) - min(data)) // round(math.log(len(data), 2), 0))

    minimum = min(data) - (min(data) % strides)
    maximum = max(data) + (max(data) % strides)

    for i in range(0, (int((maximum - minimum)) // strides)):

        price_range = str(int(minimum + (strides * i))) + '-' + str(int(minimum + (strides * (i+1))))
        graph_data[price_range] = len([price for price in data if price >= int(minimum + (strides * i)) and price < int(minimum + (strides * (i+1)))])

    return graph_data

class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)


def get_geolocation(params, GOOGLE_MAPS_API_URL = 'https://maps.googleapis.com/maps/api/geocode/json'):
    req = requests.get(GOOGLE_MAPS_API_URL, params=params)
    res = req.json()

    result = res['results'][0]
    lat = result['geometry']['location']['lat']
    lng = result['geometry']['location']['lng']

    return lat, lng



