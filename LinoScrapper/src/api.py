import codecs
import logging
import os
import re

import requests
from flask import Blueprint, request
from psycopg2.extras import Json
from lxml import html

from . import db
from .models import *



bp = Blueprint('api', __name__)

logger = logging.getLogger()
# CRAWLERA_PROXY_URL = "http://{}:@proxy.crawlera.com:8010/"

def get_request(url, crawlera_api_key=None, delay=None):
    if crawlera_api_key:
        r = requests.get(
            url,
            proxies={
                "http": CRAWLERA_PROXY_URL.format(crawlera_api_key),
                "https": CRAWLERA_PROXY_URL.format(crawlera_api_key),
            },
            verify=False,
        )
    else:
        r = requests.get(url)  # , headers={"User-Agent": ua.random})
    if delay:
        time.sleep(delay)
    r.raise_for_status()
    return r


def get_geolocation(params, GOOGLE_MAPS_API_URL = 'https://maps.googleapis.com/maps/api/geocode/json'):
    req = requests.get(GOOGLE_MAPS_API_URL, params=params)

    if req.status_code == 200:
        res = req.json()
        if len(res['results']) > 0:
            result = res['results'][0]

            Googleplace_id = result['place_id']

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

            return { 
                'civic_number': GoogleStreet_Number,
                'street': GoogleRoute,
                'city': GoogleLocality,
                'state': GoogleAdminLevel1,
                'country': GoogleCountry,
                'postal_code': GooglePostalCode,
                'latitude': GoogleLatitude,
                'longitude': GoogleLongitude
            }
        else: return "No searches found"
    else: return str(req.status_code) + " error"



def extract_values(html_content):
    tree = html.fromstring(html_content)
    title = tree.xpath('//h1[starts-with(@class, "title-")]/text()')
    title = "".join(title or [])
    price = tree.xpath('//span[starts-with(@class, "currentPrice-")]/span[1]/@content')
    if price:
        price = "".join(price)
    else:
        price = "".join(
            tree.xpath('//span[starts-with(@class, "currentPrice-")]/text()')
        )
    address = tree.xpath('//span[@itemprop="address"]/text()')
    address = "".join(address or [])
    description = tree.xpath(
        '//div[starts-with(@class, "descriptionContainer-")]//p/text()'
    )
    description = "\n".join(description) if description else None
    address = "".join(address or [])
    params = {
        'address': address.replace(' ', '+'),
        'key': 'AIzaSyA9u5PnH2nHMiFRWJRWGhtmprCuAueuB2o'
    }
    address_dict = get_geolocation(params)
    features = extract_features(tree)
    size = None
    if 'Pièces' in features.keys(): size = features['Pièces']

    return {
        "title": title,
        "price": price,
        "description": description,
        "size": size,
        "features": features,
    }, address_dict



def extract_features(tree):
    features = {}
    # Single attribute features (floating)
    for dl in tree.xpath('//dl[starts-with(@class, "itemAttribute-")]'):
        name, value = dl.xpath(".//*")
        features[name.text_content()] = value.text_content()

    # Single attribute features (in panel)
    for li in tree.xpath('//li[starts-with(@class, "realEstateAttribute-")]'):
        elems = li.xpath("./div/*")
        if elems and len(elems) == 2:
            features[elems[0].text_content()] = elems[1].text_content()

    # Attribute group features (in panel)
    for li in tree.xpath('//li[starts-with(@class, "attributeGroupContainer-")]'):
        group_title = li.xpath('.//h4[starts-with(@class, "attributeGroupTitle-")]')
        group_title = group_title[0].text_content()
        item_lis = li.xpath('.//li[starts-with(@class, "groupItem-")]')
        items = []
        for item_li in item_lis:
            is_present = item_li.xpath(".//use")[0].get("xlink:href") == "#icon-yes"
            items.append((item_li.text_content(), is_present))
        features[group_title] = items

    for li in tree.xpath('//li[starts-with(@class, "twoLinesAttribute-")]'):
        group_title = li.xpath('.//dt[starts-with(@class, "twoLinesLabel-")]')[0].text_content()
        item_lis = li.xpath('.//dd[starts-with(@class, "twoLinesValue-")]')[0].text_content()
        features[group_title] = item_lis

    return features


def extract_images(html_content, ad_id, crawlera_api_key):
    # This looks in some JS code
    image_recs = re.finditer(
        '{"type":"image","href":"(.*?)","thumbnail":".*?"}', html_content
    )
    # Convert \u002F to "/"
    img_urls = {codecs.decode(rec.group(1), "unicode-escape") for rec in image_recs}
    # output_dir = f"/images/{ad_id}"
    # if img_urls:
    #     os.makedirs(output_dir)
    n_images = len(img_urls)
    # for i, img_url in enumerate(img_urls):
    #     # Note: we don't use any delay for image downloading
    #     img_data = get_request(img_url, crawlera_api_key).content
    #     with open(os.path.join(output_dir, f"{i}.jpg"), "wb") as f:
    #         f.write(img_data)
    #         n_images += 1
    return n_images, img_urls


# @bp.route('/ads/<int:id>', methods=['GET'])
# def get_ads(id):
#     return jsonify(Ad.query.get_or_404(id).to_dict())


# @bp.route('/ads', methods=['POST'])
# def create_ad():
#     data = request.get_json() or {}
#     ad = Ad()
#     ad.from_dict(data)
#     db.session.add(ad)
#     db.session.commit()
#     response = jsonify(ad.to_dict())
#     response.status_code = 201
#     response.headers['Location'] = url_for('api.get_ads', id=ad.ad_id)
#     return response


@bp.route('/ads/extract', methods=['POST'])
def extract():

    # try:
    received_data = request.json
    ad_url = received_data['ad_url']
    crawlera_api_key = received_data['key']
    delay = received_data['delay']
    no_images = received_data['no_images']

    logger.info(f"scraping {ad_url}")
    r = get_request(ad_url, crawlera_api_key, delay)
    html_content = r.content.decode("utf8")

    ad = Ad.query.filter_by(url=ad_url).first()
    if ad is not None:
        db.session.delete(ad)
        db.session.commit()

    ad = Ad(url=ad_url)
    db.session.add(ad)
    db.session.commit()

    n_images = None  # Distinguish with 0 images
    if not no_images:
        n_images, img_urls = extract_images(html_content, ad.ad_id, crawlera_api_key)
        logger.info(f"extracted {n_images} images")

    values = {"html_content": html_content, "n_images": n_images}
    ad_dict, address_dict = extract_values(html_content)
    values.update(ad_dict)
    values["features"] = Json(values["features"])

    address_dict['ad_id'] = ad.ad_id
    address = Address()
    address.from_dict(address_dict)

    ad.from_dict(ad_dict)
    db.session.add(address)
    db.session.commit()

    # except:
    #     print("except")

    msg = f"scraped {ad_url}"

    return {'ad_id': int(ad.ad_id), 'img_urls': list(img_urls)}




