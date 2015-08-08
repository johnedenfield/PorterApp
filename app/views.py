__author__ = 'johnedenfield'

from . import app
from flask import render_template, request, flash, redirect, url_for
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from .models import BeerList, UserBeerList, BeerListUpdate, User, db
from .forms import LoginForm, RegistrationForm, RateBeerForm, DeleteRatingForm

from datetime import datetime, timedelta
from dateutil import tz

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = '/login'


# Format Functions
def datetimeformat(dte):
    format = "%m/%d/%y %H:%M"
    utc = dte.replace(tzinfo=tz.gettz('UTC'))
    local_time = utc.astimezone(tz.gettz('America/New_York'))

    return local_time.strftime(format)


def time_delta(value):
    dt = datetime.utcnow() - value
    return dt.seconds // 60

# Set Format Functions to current App
app.jinja_env.filters['datetimeformat'] = datetimeformat
app.jinja_env.filters['timedelta'] = time_delta


@login_manager.user_loader
def load_user(user_id):
    # Log in User
    user = User.query.filter(User.ID == user_id).first()
    if user is not None:
        return user


@app.route("/")
@login_required
def beer_list():
    # Returns the current beer list with the user ratings

    last_update_id = db.session.query(db.func.max(BeerListUpdate.ID)).scalar()
    updated = BeerListUpdate.query.filter(BeerListUpdate.ID == last_update_id).first()

    user_rating = db.session.query(UserBeerList.Beer_ID,
                                   db.func.avg(UserBeerList.Rating).label('Avg_Rating'),
                                   db.func.count(UserBeerList.Rating).label('Avg_Rating_cnt')). \
        filter(UserBeerList.User_ID == current_user.get_id()).group_by(UserBeerList.Beer_ID).subquery()

    # Future Implementation of other user ratings
    # other_user_rating = db.session.query(UserBeerList.Beer_ID, \
    #                                     db.func.avg(UserBeerList.Rating).label('Avg_Rating'),
    #                                     db.func.count(UserBeerList.Rating).label('Avg_Rating_cnt')). \
    #    filter(UserBeerList.User_ID != current_user.get_id()).group_by(UserBeerList.Beer_ID).subquery()

    rated_beerlist = db.session.query(BeerList.Beer_ID, BeerList.Beer, BeerList.Brewery,
                                      user_rating.c.Avg_Rating.label('AvgUserRating'),
                                      user_rating.c.Avg_Rating_cnt.label('UserRatingCnt')). \
        outerjoin(user_rating, BeerList.Beer_ID == user_rating.c.Beer_ID). \
        filter(BeerList.Update_ID == last_update_id).order_by(user_rating.c.Avg_Rating.desc()).all()

    # beer_list = db.session.query(beer_list1.c.Beer, beer_list1.c.Brewery,
    #                             beer_list1.c.AvgUserRating, beer_list1.c.UserRatingCnt,
    #                             other_user_rating.c.Avg_Rating, other_user_rating.c.Avg_Rating_cnt). \
    #    outerjoin(other_user_rating, beer_list1.c.Beer_ID == other_user_rating.c.Beer_ID).all()

    my_beer_list = []
    for beer in rated_beerlist:
        my_beer_list.append(dict(Beer_ID=beer[0], Beer=beer[1], Brewery=beer[2], UserRating=beer[3],
                                 UserRateCnt=beer[4]))

    return render_template('beer_list.html', mybeerlist=my_beer_list, current_user=current_user, updated=updated)


@app.route('/rate_beer/<Beer_ID>', methods=['GET', 'POST'])
@login_required
def rate_beer(Beer_ID):
    rate_form = RateBeerForm(request.form)

    if request.method == 'POST':

        if rate_form.validate_on_submit():

            beer_id = rate_form.beerid.data
            rating = rate_form.rating.data
            beer = UserBeerList(User_ID=current_user.get_id(), Beer_ID=beer_id, Rating=int(rating))

            db.session.add(beer)
            db.session.commit()

            return redirect(url_for('beer_list'))

        else:
            print "validation failed"
            return redirect(url_for('rate_beer', Beer_ID=Beer_ID))

    else:
        beer = BeerList.query.filter(BeerList.Beer_ID == Beer_ID).first()
        rate_form.beerid.data = Beer_ID

        return render_template('rate_beer.html', rate_form=rate_form, beer=beer)


@app.route('/delete_rating/<Beer_ID>', methods=['POST'])
@login_required
def delete_rating(Beer_ID):
    form = DeleteRatingForm(request.form)

    if form.validate_on_submit():
        UserBeerList.query.filter(UserBeerList.ID == form.id.data).delete()
        db.session.commit()

    return redirect(url_for('beer_info', Beer_ID=Beer_ID))


@app.route('/beer/<Beer_ID>', methods=['GET'])
@login_required
def beer_info(Beer_ID):
    beer = BeerList.query.filter(BeerList.Beer_ID == Beer_ID).first()

    myratings = UserBeerList.query.filter(UserBeerList.User_ID == current_user.get_id()). \
        filter(UserBeerList.Beer_ID == Beer_ID).order_by(UserBeerList.DateAndTime.desc()).all()

    delete_form = []
    for r in myratings:
        d_form = DeleteRatingForm()
        d_form.id.data = r.ID
        delete_form.append(d_form)

    # Trend Time on draft for last 30 days
    start_date = datetime.utcnow() - timedelta(days=30)

    beer_data = db.session.query(BeerListUpdate.DateAndTime). \
        join(BeerList, BeerList.Update_ID == BeerListUpdate.ID). \
        filter(BeerList.Beer_ID == Beer_ID). \
        filter(BeerListUpdate.DateAndTime > start_date). \
        order_by(BeerListUpdate.DateAndTime.asc()).all()

    on_draft_dates = []
    epoch = datetime.utcfromtimestamp(0)

    for d in xrange(0, 30):
        start_day = start_date + timedelta(days=d)
        end_day = start_date + timedelta(days=d + 1)

        n = 0
        for b in beer_data:
            if b.DateAndTime >= start_day and b.DateAndTime < end_day:
                n = 1
                break

        dt = start_day - epoch
        dts = dt.total_seconds()
        on_draft_dates.append([dts * 1000, n])

    return render_template('beer_info.html', beer=beer, on_draft=on_draft_dates,
                           myratings=myratings, delete_form=delete_form)


@app.route('/favorite', methods=['GET', 'POST'])
@login_required
def favorite():
    # List all the  beers rated by the user. Show which beers are currently on draft

    # Get User Ratings
    my_ratings = db.session.query(BeerList.Beer_ID, BeerList.Beer,
                                  db.func.max(BeerList.Update_ID).label('LastUpdate'),
                                  db.func.avg(UserBeerList.Rating).label('AvgRating')). \
        join(UserBeerList, UserBeerList.Beer_ID == BeerList.Beer_ID). \
        filter(UserBeerList.User_ID == current_user.get_id()). \
        group_by(BeerList.Beer_ID, BeerList.Beer). \
        order_by(db.func.avg(UserBeerList.Rating).desc()).all()

    # Last Update Id
    update_id = db.session.query(db.func.max(BeerListUpdate.ID)).scalar()

    return render_template('favorite.html', my_ratings=my_ratings, update_id=update_id)


# register / Login / Logout

@app.route('/register', methods=['GET', 'POST'])
def register():
    #  Creates a account user account

    form = RegistrationForm(request.form)

    if form.validate_on_submit():

        check_user = User.query.filter(User.Email == form.email.data).first()

        if check_user is None:
            new_user = User(form.username.data, form.email.data, form.password.data)
            db.session.add(new_user)
            db.session.commit()

            return redirect(url_for('login'))

        else:
            flash(form.email.data + ' is alerady regestered with a user', 'login')

    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)

    if form.validate_on_submit():

        email = form.email.data.lower()
        user = User.query.filter(User.Email == email).first()

        if user is not None and user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for('beer_list'))
        else:
            if user is None:
                flash('User\'s email: %s cannot be found. Check your email address' % email, 'login')
            else:
                flash('Incorrect Password', 'login')

            return render_template('login.html', form=form)

    else:
        return render_template('login.html', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('beer_list'))
