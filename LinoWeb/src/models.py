from src import db

# coding: utf-8
from sqlalchemy import text
from sqlalchemy.dialects.postgresql import JSONB


class Ad(db.Model):
    __tablename__ = 'ad'

    ad_id = db.Column(db.Integer, primary_key=True, server_default=text("nextval('ad_ad_id_seq1'::regclass)"))
    url = db.Column(db.Text, nullable=False, unique=True)
    scraped_at = db.Column(db.DateTime, nullable=False, server_default=text("now()"))
    html_content = db.Column(db.Text)
    n_images = db.Column(db.Integer)
    features = db.Column(JSONB(astext_type=db.Text()))
    title = db.Column(db.Text)
    price = db.Column(db.Text)
    description = db.Column(db.Text)
    address = db.Column(db.Text)
    size = db.Column(db.Text)
    address_id = db.relationship('Address', uselist=False)

    def to_dict(self):
        data = {
            'id': self.ad_id,
            'url': self.url,
            'scrapped_at': self.scraped_at,
            'html_content': self.html_content,
            'n_images': self.n_images,
            'features': self.features,
            'title': self.title,
            'price': self.price,
            'description': self.description,
            'room_number': self.room_number,
            'address_id': self.address_id,
            'size': self.size
        }
        return data

    def from_dict(self, data):
        for field in ['url', 'scrapped_at', 'html_content', 'n_images', 'features', 'title', 'price', 'description',
                      'room_number', 'size']:
            if field in data:
                setattr(self, field, data[field])

class AdBkp(db.Model):
    __tablename__ = 'ad_bkp'

    ad_id = db.Column(db.Integer, primary_key=True, server_default=db.text("nextval('ad_ad_id_seq'::regclass)"))
    url = db.Column(db.Text, nullable=False, unique=True)
    queued = db.Column(db.DateTime, nullable=False, server_default=db.text("now()"))
    visited = db.Column(db.DateTime)
    html_content = db.Column(db.Text)
    n_images = db.Column(db.Integer)


class Address(db.Model):
    __tablename__ = 'address'

    id = db.Column(db.Integer, primary_key=True)
    civic_number = db.Column(db.Text)
    street = db.Column(db.Text)
    city = db.Column(db.Text)
    state = db.Column(db.Text)
    country = db.Column(db.Text)
    postal_code = db.Column(db.Text)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    ad_id = db.Column(db.ForeignKey('ad.ad_id'))

    def to_dict(self):
        data = {
            'id': self.id,
            'civic_number': self.civic_number,
            'street': self.street,
            'city': self.city,
            'state': self.state,
            'country': self.country,
            'postal_code': self.postal_code,
            'longitude': self.longitude,
            'latitude': self.latitude,
            'ad_id': self.ad_id,
        }
        return data

    def from_dict(self, data):
        for field in ['civic_number', 'street', 'city', 'state', 'country', 'postal_code', 'longitude', 'latitude', 'ad_id']:
            if field in data:
                setattr(self, field, data[field])