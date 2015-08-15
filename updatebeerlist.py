__author__ = 'johnedenfield'

from lxml import html
import requests
from datetime import datetime
from app.models import db, DraftList, DraftHistory
from sqlalchemy import update


def scrape_draft_list():
    r = requests.get('http://www.theporterbeerbar.com/drink/beer')
    tree = html.fromstring(r.text)
    beer_table = tree.find_class("beerListTable")
    beers = beer_table[0].find_class('datarow')

    dte = datetime.utcnow()

    for tr in beers:
        brewery = tr[0].text.strip()

        url = ''
        if len(tr[1]) == 1:
            a = tr[1][0]
            beer = a.text.strip()
            url = a.get('href')
        else:
            beer = tr[1].text.strip()

        style = tr[2].text.strip()
        origin = tr[3].text.strip()
        volume = tr[4].text.strip()
        abv = tr[5].text.strip()
        description = tr[6].text.strip()

        beer_id = ''.join(e for e in brewery + beer if e.isalnum()).upper()

        if 'beeradvocate' in url:
            rating = scrape_beer_advocate(url)

        elif 'ratebeer' in url:
            rating = scrape_rate_beer(url)

        draft_beer = DraftList.query.filter(DraftList.Beer_ID == beer_id).first()


        if draft_beer is None:
            draft_beer = DraftList(Beer_ID=beer_id, OnDraft=1, Updated=dte, Brewery=brewery,
                                   Beer=beer, Style=style, Origin=origin, Volume=volume, ABV=abv,
                                   Description=description, BeerRating=rating,
                                   RatingSite=url, NotifyUser=1)
        else:

            if draft_beer.OnDraft == 0:
                draft_beer.NotifyUser = 1

            draft_beer.OnDraft = 1
            draft_beer.Updated = dte
            draft_beer.Style = style
            draft_beer.Origin = origin
            draft_beer.Volume = volume
            draft_beer.ABV = abv
            draft_beer.Description = description
            draft_beer.BeerRating = rating
            draft_beer.RatingSite = url

        db.session.add(draft_beer)

        draft_history = DraftHistory(DateAndTime=dte, Beer_ID=beer_id)
        db.session.add(draft_history)

    db.session.commit()

    draft_list = DraftList.query.filter(DraftList.Updated != dte).all()
    for beer in draft_list:
        beer.OnDraft = 0
        db.session.add(beer)

    db.session.commit()


def scrape_beer_advocate(url):
    try:
        r = requests.get(url)
    except:
        return None

    tree = html.fromstring(r.text)

    r = tree.xpath('//span[@class="BAscore_big ba-score"]')

    try:
        rating_str = r[0].text
        rating = float(rating_str)
    except:
        rating = None

    return rating


def scrape_rate_beer(url):
    try:
        r = requests.get(url)
    except:
        return None

    tree = html.fromstring(r.text)
    r = tree.xpath('//span[@itemprop="average"]')

    try:
        rating_str = r[0].text
        rating = float(rating_str)
    except:
        rating = None

    return rating


if __name__ == "__main__":
    scrape_draft_list()
