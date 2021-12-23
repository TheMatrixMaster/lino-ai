# -*- coding: utf-8 -*-
# @Author: stephen.zlu
# @Date:   2019-09-11 10:32:13
# @Last Modified by:   slu13
# @Last Modified time: 2019-09-27 23:10:06

import functools
from flask import (
    Blueprint,
    session,
    redirect,
    url_for,
    flash,
    abort,
    request,
    render_template,
)

from . import db
from .models import *
from .functions import *

import requests
from math import cos, asin, sqrt
import cv2
import json


bp = Blueprint('view', __name__)



def distance(lat1, lon1, lat2, lon2):
    p = 0.017453292519943295
    a = 0.5 - cos((lat2-lat1)*p)/2 + cos(lat1*p)*cos(lat2*p) * (1-cos((lon2-lon1)*p)) / 2
    return 12742 * asin(sqrt(a))

def closest(data, v):
    closest = min(data, key=lambda p: distance(v['lat'],v['lon'],p['lat'],p['lon']))
    index = data.index(closest)
    return index


icons = {
        'Housing type': "far fa-building",
        'Bathrooms': "fas fa-toilet",
        'Services': "fas fa-tint",
        'Parking': "fas fa-parking",
        'Lease term': "far fa-clock",
        'Moving date': "far fa-calendar-alt",
        'Size': "fas fa-ruler",
        'Furniture': "fas fa-couch",
        'Appliances': "fas fa-bath",
        'Air conditioning': "far fa-snowflake",
        'Private outdoor areas': "fas fa-warehouse"
    }



### SHARED TEMPLATES

@bp.route('/', methods=['GET', 'POST'])
@bp.route('/home', methods=['GET', 'POST'])
def home():
    return render_template('home.html')



@bp.route('/general', methods=['GET'])
def general():

    img_links = session['img_links']
    ad_id = session['ad_id']
    prices = session['prices']

    header_info, general_info, housing_info, building_info, description = fake_webscraper()

    my_ad = Ad.query.filter_by(ad_id=ad_id).first()

    graph_data = create_graph_data(prices)
    exact_avg_price = round(sum(prices)/len(prices), 2)
    exact_my_price = float(my_ad.price)
    my_price = [key for key in graph_data.keys() if 
                exact_my_price >= int(key.split('-')[0]) and 
                exact_my_price < int(key.split('-')[1])][0]

    avg_price = [key for key in graph_data.keys() if 
                exact_avg_price >= int(key.split('-')[0]) and 
                exact_avg_price < int(key.split('-')[1])][0]


    """Google Maps API to geolocalize address_id"""
    lat = my_ad.address_id.latitude
    lng = my_ad.address_id.longitude

    return render_template('results.html',
                            ad=my_ad,
                            header_info=header_info,
                            icons=icons,
                            general_info=general_info,
                            housing_info=housing_info,
                            building_info=building_info,
                            description=description,
                            graph_data=graph_data,
                            exact_my_price=exact_my_price,
                            exact_avg_price=exact_avg_price,
                            my_price=my_price,
                            avg_price=avg_price,
                            lat=lat,
                            lng=lng)
    


@bp.route('/room-classification', methods=['GET'])
def room_classification():

    img_links = session['img_links']

    """Room Classification Model"""
    room_pred = {}
    for i, link in enumerate(img_links):
        arr = cv2.imdecode(np.asarray(bytearray(requests.get(link).content), dtype=np.uint8), -1)
        data = {'model': 'RoomNet', 'arr': arr.tolist()}
        r = requests.post('http://127.0.0.1:5100/room_prediction', json=data)

        if r.text in room_pred.keys(): room_pred[r.text].append(img_links[i])
        elif r.text not in room_pred.keys():
            room_pred[r.text] = []
            room_pred[r.text].append(img_links[i])

    if 'Kitchen' in room_pred.keys(): session['kitchen_links'] = room_pred['Kitchen']
    else: session['kitchen_links'] = None

    return render_template('room_classification.html', room_pred=room_pred)


@bp.route('/kitchen-classification', methods=['GET'])
def kitchen_classification():

    img_links = session['kitchen_links']

    """Kitchen Hood Classification Model"""
    kitchen_pred = {}
    for i, link in enumerate(img_links):
        arr = cv2.imdecode(np.asarray(bytearray(requests.get(link).content), dtype=np.uint8), -1)
        data = {'model': 'KitchenNet', 'arr': arr.tolist()}
        r = requests.post('http://127.0.0.1:5100/kitchen_prediction', json=data)

        if r.text in kitchen_pred.keys(): kitchen_pred[r.text].append(img_links[i])
        elif r.text not in kitchen_pred.keys():
            kitchen_pred[r.text] = []
            kitchen_pred[r.text].append(img_links[i])

    return render_template('kitchen_classification.html', kitchen_pred=kitchen_pred)


@bp.route('/object-detection', methods=['GET'])
def object_detection():
    return render_template('object_detection.html')


# LOCATAIRE


@bp.route('/search', methods=['GET', 'POST'])
def search():
    
    if request.method == 'POST':
        real_estate_url = str(request.form.get('search'))

        # Call to API pour envoyer une numpy image en json

        data = {"ad_url": real_estate_url, "key": None, "delay": None, "no_images": False}
        r = requests.post('http://127.0.0.1:5000/ads/extract', json=data)

        data = r.json()
        ad_id = data['ad_id']
        img_links = data['img_urls']

        # Coordinate Comparison Module
        target = Ad.query.filter_by(ad_id=ad_id).first()
        target_size = str(target.size).strip()

        target_coords = {'lat': target.address_id.latitude, 'lon': target.address_id.longitude}
        target_price = target.price
        print(len(Ad.query.filter(Ad.address_id.has()).all()))
        query_ads = Ad.query.filter(Ad.address_id.has()).filter(Ad.features.has_key('Pièces')).filter(Ad.features['Pièces'].astext == target_size).all()
        print(len(query_ads))

        query_ad_ids = [ ad.ad_id for ad in query_ads]
        query_ad_coords = [ {'lat': ad.address_id.latitude, 'lon': ad.address_id.longitude} for ad in query_ads ]

        print(len(query_ad_ids), len(query_ad_coords))

        list_of_prices = []
        for i in range(15):
            index = closest(query_ad_coords, target_coords)
            list_of_prices.append(float(Ad.query.filter_by(ad_id = query_ad_ids[index]).first().price))
            del query_ad_ids[index]
            del query_ad_coords[index]

        session['prices'] = list_of_prices
        session['ad_id'] = ad_id
        session['img_links'] = img_links

        return(redirect(url_for('view.general')))

    return render_template('searchbar.html')





### PROPRIETAIRE 

@bp.route('/form', methods=['GET', 'POST'])
def form():

    if request.method == 'POST':
        address_id = request.form['adresse']
        num_rooms = request.form['number_rooms']
        size = request.form['taille']

        print(address_id, num_rooms, size)

        return redirect(url_for('view.pictures'))

    return render_template('form.html')

@bp.route('/pictures', methods=['GET', 'POST'])
def pictures():

    if request.method == 'POST':
        print(request.files)
        if 'files' not in request.files:
            print('No file part')
            return redirect(request.url)

        files = request.files.getlist("files")
        for file in files:
            if file.filename == '':
                print('No file selected')
                return redirect(request.url)

            if file.filename:
                print('Success')
                print(file.filename)
                # db.session.add(File(
                #     key=secure_filename(file.filename),
                #     desc=request.form['desc'],
                #     data=file,
                # ))
                # db.session.commit()
                # flash('success')

        return redirect(url_for('view.proprietaire'))

    return render_template('pictures.html')


