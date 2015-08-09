__author__ = 'johnedenfield'

import sys, os 

#VER_ENV_DIR ="/var/www/Flask/Apps/PorterApp/env"

# Activate virtural env
#activate_this = os.path.join(VER_ENV_DIR, 'bin', 'activate_this.py')
#execfile(activate_this, dict(__file__=activate_this))


from lxml import html
import requests
from datetime import datetime
from app.models import db, BeerListUpdate, BeerList



r = requests.get('http://www.theporterbeerbar.com/drink/beer')
tree =html.fromstring(r.text)
beertable =tree.find_class("beerListTable")

data=[]
today=datetime.now()

beer_list_update=BeerListUpdate(DateAndTime=datetime.utcnow())
db.session.add(beer_list_update)
db.session.commit()

for tr in beertable[0].iter(tag="tr"):

    if tr[0].tag == 'td':
        beer = tr[1][0].text.strip()
        brewery = tr[0].text.strip()
        id=''.join(e for e in brewery + beer if e.isalnum()).upper()

        data.append(
            BeerList(Update_ID=beer_list_update.ID, Beer_ID=id, Brewery=brewery, Beer=tr[1][0].text, Style=tr[2].text,
                Origin =tr[3].text, Volume=tr[4].text, ABV =tr[5].text, Description = tr[6].text))


db.session.add_all(data)
db.session.commit()


# Deactivatre virtural env
#os.system('deactivate')





