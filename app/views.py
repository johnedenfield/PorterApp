__author__ = 'johnedenfield'

from . import app
from flask import render_template, request, flash, redirect, url_for
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from .models import DraftList, UserBeerList, DraftHistory, User, db
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
def index():
    return redirect(url_for('draft_list'))


@app.route("/on_draft")
@login_required
def draft_list():
    # Returns the current beer list with the user ratings
    updated = db.session.query(db.func.max(DraftList.Updated)).filter(DraftList.OnDraft == 1).scalar()

    my_rating = db.session.query(UserBeerList.Beer_ID,
                                 db.func.avg(UserBeerList.Rating).label('Avg_Rating'),
                                 db.func.count(UserBeerList.Rating).label('Avg_Rating_cnt')) \
        .group_by(UserBeerList.Beer_ID). \
        filter(UserBeerList.User_ID == current_user.get_id()).subquery()

    others_rating = db.session.query(UserBeerList.Beer_ID,
                                     db.func.avg(UserBeerList.Rating).label('Avg_Rating'),
                                     db.func.count(UserBeerList.Rating).label('Avg_Rating_cnt')). \
        group_by(UserBeerList.Beer_ID). \
        filter(UserBeerList.User_ID != current_user.get_id()).subquery()

    rated_draft_list = db.session.query(DraftList.Beer_ID, DraftList.Beer, DraftList.Brewery,
                                        DraftList.BeerRating, DraftList.RatingSite,
                                        my_rating.c.Avg_Rating.label('MyRating'),
                                        my_rating.c.Avg_Rating_cnt.label('MyRatingCnt'),
                                        others_rating.c.Avg_Rating.label('OtherRating'),
                                        others_rating.c.Avg_Rating_cnt.label('OtherRatingCnt')). \
        filter(DraftList.OnDraft == 1). \
        outerjoin(my_rating, DraftList.Beer_ID == my_rating.c.Beer_ID). \
        outerjoin(others_rating, DraftList.Beer_ID == others_rating.c.Beer_ID). \
        order_by(my_rating.c.Avg_Rating.desc(), DraftList.BeerRating.desc()).all()

    draft_list = [dict(Beer_ID=beer[0], Beer=beer[1], Brewery=beer[2],
                       BeerRating=beer[3], RatingSite=beer[4],
                       MyRating=beer[5], MyRateCnt=beer[6], OthersRating=beer[7],
                       OthersRateCnt=beer[8]) for beer in rated_draft_list]

    return render_template('draft_list.html', draft_list=draft_list, current_user=current_user, updated=updated)


@app.route("/all_drafts")
@login_required
def all_drafts():
    # Returns the current beer list with the user ratings

    my_rating = db.session.query(UserBeerList.Beer_ID,
                                 db.func.avg(UserBeerList.Rating).label('Avg_Rating'),
                                 db.func.count(UserBeerList.Rating).label('Avg_Rating_cnt')) \
        .group_by(UserBeerList.Beer_ID). \
        filter(UserBeerList.User_ID == current_user.get_id()).subquery()

    others_rating = db.session.query(UserBeerList.Beer_ID,
                                     db.func.avg(UserBeerList.Rating).label('Avg_Rating'),
                                     db.func.count(UserBeerList.Rating).label('Avg_Rating_cnt')). \
        group_by(UserBeerList.Beer_ID). \
        filter(UserBeerList.User_ID != current_user.get_id()).subquery()

    rated_draft_list = db.session.query(DraftList.Beer_ID, DraftList.Beer, DraftList.Brewery,
                                        DraftList.BeerRating, DraftList.RatingSite,
                                        DraftList.OnDraft,
                                        my_rating.c.Avg_Rating.label('MyRating'),
                                        my_rating.c.Avg_Rating_cnt.label('MyRatingCnt'),
                                        others_rating.c.Avg_Rating.label('OtherRating'),
                                        others_rating.c.Avg_Rating_cnt.label('OtherRatingCnt')). \
        outerjoin(my_rating, DraftList.Beer_ID == my_rating.c.Beer_ID). \
        outerjoin(others_rating, DraftList.Beer_ID == others_rating.c.Beer_ID). \
        order_by(DraftList.Brewery).all()

    draft_list = [dict(Beer_ID=beer[0], Beer=beer[1], Brewery=beer[2],
                       BeerRating=beer[3], RatingSite=beer[4], OnDraft=beer[5],
                       MyRating=beer[6], MyRateCnt=beer[7], OthersRating=beer[8],
                       OthersRateCnt=beer[9]) for beer in rated_draft_list]

    return render_template('all_drafts.html', draft_list=draft_list, current_user=current_user)


@app.route('/rate_beer/<this_beer>', methods=['GET', 'POST'])
@login_required
def rate_beer(this_beer):
    rate_form = RateBeerForm(request.form)

    if request.method == 'POST':

        if rate_form.validate_on_submit():

            beer_id = rate_form.beerid.data
            rating = rate_form.rating.data
            beer = UserBeerList(User_ID=current_user.get_id(), Beer_ID=beer_id, Rating=int(rating))

            db.session.add(beer)
            db.session.commit()

            return redirect(url_for('draft_list'))

        else:
            print "validation failed"
            return redirect(url_for('rate_beer', Beer_ID=this_beer))

    else:
        beer = DraftList.query.filter(DraftList.Beer_ID == this_beer).first()
        rate_form.beerid.data = this_beer

        return render_template('rate_beer.html', rate_form=rate_form, beer=beer)


@app.route('/delete_rating/<this_beer>', methods=['POST'])
@login_required
def delete_rating(this_beer):
    form = DeleteRatingForm(request.form)

    if form.validate_on_submit():
        UserBeerList.query.filter(UserBeerList.ID == form.id.data).delete()
        db.session.commit()

    return redirect(url_for('beer_info', this_beer=this_beer))


@app.route('/beer/<this_beer>', methods=['GET'])
@login_required
def beer_info(this_beer):
    beer = DraftList.query.filter(DraftList.Beer_ID == this_beer).first()

    my_ratings = UserBeerList.query.filter(UserBeerList.User_ID == current_user.get_id()). \
        filter(UserBeerList.Beer_ID == this_beer).order_by(UserBeerList.DateAndTime.desc()).all()

    delete_form = []
    for r in my_ratings:
        d_form = DeleteRatingForm()
        d_form.id.data = r.ID
        delete_form.append(d_form)

    # Trend Time on draft for last 30 days
    start_date = datetime.utcnow() - timedelta(days=30)

    draft_history = DraftHistory.query.filter(DraftHistory.Beer_ID == this_beer). \
        filter(DraftHistory.DateAndTime > start_date).all()

    on_draft_dates = []
    epoch = datetime.utcfromtimestamp(0)

    for d in xrange(0, 30):
        start_day = start_date + timedelta(days=d)
        end_day = start_date + timedelta(days=d + 1)

        n = 0
        for record in draft_history:
            if record.DateAndTime >= start_day and record.DateAndTime < end_day:
                n = 1
                break

        dt = start_day - epoch
        dts = dt.total_seconds()
        on_draft_dates.append([dts * 1000, n])

    return render_template('beer_info.html', beer=beer, on_draft=on_draft_dates,
                           my_ratings=my_ratings, delete_form=delete_form)


@app.route('/favorite', methods=['GET', 'POST'])
@login_required
def favorite():
    # List all the  beers rated by the user. Show which beers are currently on draft

    # Get User Ratings
    my_rating = db.session.query(UserBeerList.Beer_ID,
                                 db.func.avg(UserBeerList.Rating).label('Avg_Rating'),
                                 db.func.count(UserBeerList.Rating).label('Avg_Rating_cnt')). \
        filter(UserBeerList.User_ID == current_user.get_id()).group_by(UserBeerList.Beer_ID).subquery()

    drafts = db.session.query(DraftList.Beer_ID,
                              DraftList.Beer,
                              DraftList.Brewery,
                              DraftList.BeerRating,
                              DraftList.RatingSite,
                              DraftList.OnDraft,
                              my_rating.c.Avg_Rating,
                              my_rating.c.Avg_Rating_cnt). \
        join(my_rating, my_rating.c.Beer_ID == DraftList.Beer_ID). \
        order_by(my_rating.c.Avg_Rating.desc()).all()

    favorite_drafts = [dict(Beer_ID=beer[0], Beer=beer[1], Brewery=beer[2], BeerRating=beer[3],
                            RatingSite=beer[4], OnDraft=beer[5], MyRating=beer[6]) for beer in drafts]

    return render_template('favorite.html', favorite_drafts=favorite_drafts)


@app.route('/brewery/<this_brewery>', methods=['GET', 'POST'])
@login_required
def brewery(this_brewery):
    # Get User Ratings

    my_rating = db.session.query(UserBeerList.Beer_ID,
                                 db.func.avg(UserBeerList.Rating).label('MyAvgRating')). \
        filter(UserBeerList.User_ID == current_user.get_id()).group_by(UserBeerList.Beer_ID).subquery()

    others_rating = db.session.query(UserBeerList.Beer_ID,
                                     db.func.avg(UserBeerList.Rating).label('OthersAvgRating')). \
        filter(UserBeerList.User_ID != current_user.get_id()).group_by(UserBeerList.Beer_ID).subquery()

    brewery_list = db.session.query(DraftList.Beer_ID, DraftList.OnDraft,
                                    DraftList.Beer, DraftList.BeerRating, DraftList.RatingSite,
                                    my_rating.c.MyAvgRating, others_rating.c.OthersAvgRating). \
        filter(DraftList.Brewery == this_brewery). \
        outerjoin(my_rating, my_rating.c.Beer_ID == DraftList.Beer_ID). \
        outerjoin(others_rating, others_rating.c.Beer_ID == DraftList.Beer_ID).all()

    return render_template('brewery.html', brewery_list=brewery_list, this_brewery=this_brewery)


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
            return redirect(url_for('draft_list'))
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
    return redirect(url_for('draft_list'))
