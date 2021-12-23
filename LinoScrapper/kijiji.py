import codecs
import datetime as dt
import logging
from pprint import pprint
import os
import re
import shutil
import time

import click
from tqdm import tqdm

# from fake_useragent import UserAgent
from little_pger import LittlePGer
from lxml import html
import psycopg2
from psycopg2.extras import Json
import requests


requests.packages.urllib3.disable_warnings()

AD_LISTING_URL = "https://www.kijiji.ca/b-immobilier/grand-montreal/c34l80002"
CRAWLERA_PROXY_URL = "http://{}:@proxy.crawlera.com:8010/"

# ua = UserAgent()
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("/python/kijiji.log"), logging.StreamHandler()],
)
logger = logging.getLogger()


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


def extract_images(html_content, ad_id, crawlera_api_key):
    # This looks in some JS code
    image_recs = re.finditer(
        '{"type":"image","href":"(.*?)","thumbnail":".*?"}', html_content
    )
    # Convert \u002F to "/"
    img_urls = {codecs.decode(rec.group(1), "unicode-escape") for rec in image_recs}
    output_dir = f"/images/{ad_id}"
    if img_urls:
        os.makedirs(output_dir)
    n_images = 0
    for i, img_url in enumerate(img_urls):
        # Note: we don't use any delay for image downloading
        img_data = get_request(img_url, crawlera_api_key).content
        with open(os.path.join(output_dir, f"{i}.jpg"), "wb") as f:
            f.write(img_data)
            n_images += 1
    return n_images


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
    features = extract_features(tree)
    return {
        "title": title,
        "price": price,
        "address": address,
        "description": description,
        "features": features,
    }


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

    return features


@click.group()
def cli():
    pass


@cli.command()
def resetdb():
    with LittlePGer("dbname=root host=db", commit=True) as db:
        db.sql(
            """
                  alter sequence if exists ad_ad_id_seq restart with 1;
                  drop table if exists ad cascade;
                  create table ad (
                      ad_id serial primary key,
                      url text unique not null,
                      scraped_at timestamp not null default now(),
                      html_content text,
                      n_images int,
                      title text,
                      price text,
                      address text,
                      description text,
                      features jsonb
                  );
        """
        )
    logger.info("Recreated the database")


@cli.command()
def reextract_values():
    with LittlePGer("dbname=root host=db", commit=True) as db:
        ads = db.select("ad", where={("html_content", "is not"): None})
        for ad in tqdm(ads):
            values = extract_values(ad["html_content"])
            values["features"] = Json(values["features"])
            db.update("ad", values=values, where={"ad_id": ad["ad_id"]})
    logger.info(f"Reextracted values for {len(ads)} ads")


@cli.command()
@click.option(
    "--crawlera-api-key", help="Crawlera API key (if None, no proxy will be used)"
)
@click.option(
    "--delay",
    "-d",
    default=30,
    help="Delay between requests in seconds (default 30s)",
    show_default=True,
)
@click.option(
    "--no-images",
    is_flag=True,
    help="Disable image downloading and storing",
    show_default=True,
)
def scrape(crawlera_api_key, delay, no_images):
    n_ads_scraped = 0
    stopped_early = False
    try:
        r = get_request(AD_LISTING_URL, crawlera_api_key, delay)
        tree = html.fromstring(r.content)
        for div in tree.xpath('//div[contains(@class, "regular-ad")]'):
            ad_url = "https://kijiji.ca" + div.get("data-vip-url")
            with LittlePGer("dbname=root host=db", commit=True) as db:
                try:
                    ad = db.insert("ad", values={"url": ad_url})
                except psycopg2.errors.UniqueViolation:
                    stopped_early = True
                    break

            logger.info(f"scraping {ad_url}")
            r = get_request(ad_url, crawlera_api_key, delay)
            html_content = r.content.decode("utf8")
            n_images = None  # Distinguish with 0 images
            if not no_images:
                n_images = extract_images(html_content, ad["ad_id"], crawlera_api_key)
                logger.info(f"extracted {n_images} images")
            with LittlePGer("dbname=root host=db", commit=True) as db:
                values = {"html_content": html_content, "n_images": n_images}
                values.update(extract_values(html_content))
                values["features"] = Json(values["features"])
                db.update("ad", values=values, where={"ad_id": ad["ad_id"]})
                n_ads_scraped += 1
    except Exception as e:
        logger.exception("error occurred")
        exit(1)
    msg = f"scraped {n_ads_scraped} ads"
    if stopped_early:
        msg += ", stopped early"
    logger.info(msg)


@cli.command()
@click.argument("ad_url")
@click.option(
    "--crawlera-api-key", help="Crawlera API key (if None, no proxy will be used)"
)
def test(ad_url, crawlera_api_key):
    r = get_request(ad_url, crawlera_api_key)
    values = extract_values(r.content)
    pprint(values)


if __name__ == "__main__":
    cli()
