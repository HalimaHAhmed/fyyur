#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for,jsonify
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migarate = Migrate(app,db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

#region venue model
class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120)) 
    generess = db.Column(db.String(90))
    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    seeking_talent = db.Column(db.String(80))
    seeking_description = db.Column(db.String(85))
    shows = db.relationship('Show',backref='venue',lazy=True)
    website = db.Column(db.String(87))


#endregion


#region Artist model
class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    seekking_venu = db.Column(db.String(92))
    seeking_description = db.Column(db.String(99))
    shows = db.relationship('Show',backref='artist',lazy=True)
    website = db.Column(db.String(87))
# endregion



#region show model
# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Show(db.Model):
 __tablename__ = 'show'
 id = db.Column(db.Integer,primary_key=True,nullable=False
 )
 artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'),nullable=False)
 venu_id = db.Column(db.Integer,db.ForeignKey('venue.id'),nullable=False)
 start_time = db.Column(db.DateTime,default=datetime.now(),nullable=False)

# endregion




#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#
#region controlls
@app.route('/')
def index():
  return render_template('pages/home.html')

#region venues
#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  data=[]
  mycities= db.session.query(Venue.city,Venue.state).distinct(
    Venue.city,Venue.state
  )
  for city in mycities:
    venues = db.session.query(Venue.id,Venue.name).filter(Venue.city==city[0]).filter(Venue.state==city[1])

    data.append({
      'city':city[0],
      'state':city[1],
       'venues':venues

    })
      

   
    


  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"



  search_keyword = request.form.get('search_term','')
  venues= db.session.query(Venue).filter(Venue.name.ilike(f"%{search_keyword}%")).all()
  
  data = []
  num_upcoming_shows = 0

  for venue in venues:
    shows = db.session.query(Show).filter(Show.venu_id == venue.id)
    for show in shows:
      if show.start_time > datetime.now():
        num_upcoming_shows +=1

    data.append({
      'id':venue.id,
      'name': venue.name,
      'num_upcoming_shows':num_upcoming_shows}
    )
  response={
    "count": len(venues),
    "data":data
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)
  # Registering / Create Venue

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  error = False
  try:
    name = request.form.get('name')
    city = request.form.get('city')
    address = request.form.get('address')
    phone = request.form.get('phone')
    genres = request.form.get('genres')
    facebook_link = request.form.get('facebook_link')
    image_link = request.form.get('image_link')
    website = request.form.get('website_link')
    seeking_talent = request.form.get('seeking_talent')
    seeking_description = request.form.get('seeking_description')
    # TODO: modify data to be the data object returned from db insertion
    new_venu = Venue(name=name,city=city,address=address,phone=phone,generess=genres,facebook_link=facebook_link,image_link=image_link,seeking_talent=seeking_talent,seeking_description=seeking_description,website=website)
    db.session.add(new_venu)
    db.session.commit()
  except:
      error=True
      db.session.rollback()
  finally:
      db.session.close()

  if not error:
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
  else:
      flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
  # on successful db insert, flash success
  # flash('Venue ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  data =[]

  upcoming_shows = []
  upcoming_shows_count =0

  past_shows = []
  past_shows_count=0

  venu = db.session.query(Venue).filter(Venue.id == venue_id).first()
  shows = db.session.query(Show).filter(Show.venu_id == venue_id).all()
  

  for show in shows:
    arts = db.session.query(Artist).filter(Artist.id == show.artist_id).first()
    if show.start_time > datetime.now():
      upcoming_shows_count +=1
      upcoming_shows.append({
        'artist_id': arts.id,
        'artist_name':arts.name,
        'artist_image_link':arts.image_link,
        'start_time':format_datetime(str(show.start_time))
      })
    else:
      past_shows_count +=1
      past_shows.append({
        'artist_id': arts.id,
        'artist_name':arts.name,
        'artist_image_link':arts.image_link,
        'start_time':format_datetime(str(show.start_time))
      })

  data.append({
    'id': venu.id,
    'name':venu.name,
    'city': venu.city,
    'state':venu.state,
    'address':venu.address,
    'phone': venu.phone,
    'facebook':venu.facebook_link,
    'genres':venu.generess.split(','),
    'seeking_talent':venu.seeking_talent,
    'seeking_description':venu.seeking_description,
    'website':venu.website,
    'upcoming_shows':upcoming_shows,
    'upcoming_shows_count':upcoming_shows_count,
    'past_shows':past_shows,
    'past_shows_count':past_shows_count,
    'image_link':venu.image_link

  })
  return render_template('pages/show_venue.html',venue=list(data)[0])

#endregion



#region Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database

  data = []
  artists =db.session.query(Artist).all()

  for artist in artists:
    data.append({'id':artist.id,'name':artist.name})

  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".

  search_keyword = request.form.get('search_term','')
  artists= db.session.query(Artist).filter(Artist.name.ilike(f"%{search_keyword}%")).all()
  
  data = []
  num_upcoming_shows = 0

  for artist in artists:
    shows = db.session.query(Show).filter(Show.id == artist.id)
    for show in shows:
      if show.start_time > datetime.now():
        num_upcoming_shows +=1
    data.append({
      'id':artist.id,
      'name':artist.name,
      'num_upcoming_shows':num_upcoming_shows
    })


  response={
    "count": len(artists),
    "data": data
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  data=[]
  artist = db.session.query(Artist).filter(Artist.id == artist_id).first()
  shows = db.session.query(Show).filter(Show.artist_id == artist_id).all()

  upcomming_shows =[]
  upcomming_shows_count=0

  past_shows=[]
  past_shows_count=0

  for show in shows:
    venue = db.session.query(Venue).filter(Venue.id == show.venu_id).first()
    if show.start_time > datetime.now():
      upcomming_shows_count +=1
      upcomming_shows.append({
        "venue_id": venue.id,
        "venue_name":venue.name,
        "venue_image_link":venue.image_link,
        "start_time":format_datetime(str(show.start_time))
      })
    else :
      past_shows_count +=1
      past_shows.append({
        "venue_id": venue.id,
        "venue_name":venue.name,
        "venue_image_link":venue.image_link,
         "start_time":format_datetime(str(show.start_time))
      })
  data.append({
      'id':artist.id,
      'name':artist.name,
      'genres':artist.genres.split(','),
      'city':artist.city,
      'state':artist.state,
      'phone':artist.phone,
      'website':artist.website,
      'facebook_link':artist.facebook_link,
      "seeking_venue": artist.seekking_venu,
      "seeking_description": artist.seeking_description,
      "image_link":artist.image_link,
      "past_shows":past_shows,
      "upcoming_shows":upcomming_shows,
      "past_shows_count":past_shows_count,
      "upcoming_shows_count":upcomming_shows_count,
    })

  # data = list(filter(lambda d: d['id'] == artist_id, [data]))[0]
  return render_template('pages/show_artist.html', artist=list(data)[0])

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = db.session.query(Artist).filter(Artist.id == artist_id).first()
  form = ArtistForm(obj=artist)
  artist= {
    'id':artist.id,
    'name':artist.name,
    'city':artist.city,
    'state':artist.state,
    'phone':artist.phone,
    'genres':artist.genres,
    'iamge_link':artist.image_link,
    'facebooklink':artist.facebook_link,
    'seeking_venue':artist.seekking_venu,
    'seeking_description':artist.seeking_description,
    'website':artist.website
   
 }
  
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  artist = db.session.query(Artist).filter(Artist.id == artist_id).first()

  print(artist)
  artist.name = request.form.get('name')
  artist.genres = ",".join(request.form.getlist('genres'))
  artist.city = request.form.get('city')
  artist.state = request.form.get('state')
  artist.phone = request.form.get('phone')
  artist.website = request.form.get('website')
  artist.image_link = request.form.get('image_link')
  artist.facebook_link = request.form.get('facebook_link')
  artist.seekking_venue = True if request.form.get('seeking_venue') != None else False
  artist.seeking_description = request.form.get('seeking_link')
  artist.image_link = request.form.get('image_link')
  db.session.commit()

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
 
  venu = db.session.query(Venue).filter(Venue.id==venue_id).first()
  form = VenueForm(obj=venu)
  venu ={
    'id':venu.id,
    'name':venu.name,
    'city':venu.city,
    'state':venu.state,
    'address':venu.address,
    'phone':venu.phone,
    'image_link':venu.image_link,
    'face_link':venu.facebook_link,
    'generes':venu.generess,
    'seeking_talent':venu.seeking_talent,
    'seeking_description':venu.seeking_description,
    'website':venu.website

     
  }
 
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venu)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes

  venue = db.session.query(Venue).filter(Venue.id ==venue_id).first()
  venue.name = request.form.get('name')
  venue.city = request.form.get('city')
  venue.state = request.form.get('state')
  venue.address = request.form.get('address')
  venue.phone = request.form.get('phone')
  venue.image_link = request.form.get('image_link')
  venue.facebook_link = request.form.get('facebooklink')
  venue.generess =request.form.getlist('genres')
  venue.seekking_talent = True if request.form.get('seeking_talent') != None else False
  venue.seeking_description = request.form.get('seeking description')
  venue.website = request.form.get('website')
  db.session.commit()




  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead

  # TODO: modify data to be the data object returned from db insertion



  error = False
  # try:
  name = request.form.get('name')
  city = request.form.get('city')
  # address = request.form.get('address')
  phone = request.form.get('phone')
  genres = request.form.get('genres')
  facebook_link = request.form.get('facebook_link')
  image_link = request.form.get('image_link')
  website = request.form.get('website_link')
  seekking_venu = request.form.get('seekking_venue')
  seeking_description = request.form.get('seeking_description')
    # TODO: modify data to be the data object returned from db insertion
  new_artist = Artist(name=name,city=city,phone=phone,genres=genres,facebook_link=facebook_link,image_link=image_link,seekking_venu=seekking_venu,seeking_description=seeking_description,website=website)
  db.session.add(new_artist)
  db.session.commit()
  # except:
  #   error=True
  #   db.session.rollback()
  # finally:
  #   db.session.close()  

   # on successful db insert, flash success
  flash('Artist ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')


#endregion

# Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  data=[]

  shows = db.session.query(Show).all()
  for show in shows:
    artist = db.session.query(Artist.id, Artist.name,Artist.image_link).filter(Artist.id == show.artist_id).first()
    venue = db.session.query(Venue.id,Venue.name).filter(Venue.id == show.venu_id).first()

    data.append({
      "venue_id":venue.id,
      "venue_name":venue.name,
      "artist_id":artist.id,
      "artist_name":artist.name,
      "artist_image_link":artist.image_link,
      "start_time":format_datetime(str(show.start_time))
    })
    



  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  error = False
  try:
      artist_id = request.form.get('artist_id')
      venue_id = request.form.get('venue_id')
      start_time=request.form.get('start_time')
    
      # TODO: modify data to be the data object returned from db insertion
      newpast_show = Show(artist_id=artist_id,venu_id=venue_id,start_time=start_time)
      db.session.add(newpast_show)
      db.session.commit()
      
  except:
      error=True
      db.session.rollback()
  finally:
      # db.session.close()
      pass

  if not error:
      flash('show ' +request.form.get('artist_id') + ' was successfully listed!')
  else:
      flash('An error occurred. Venue ' + request.form.get('artist_id') + ' could not be listed.')
  return redirect(url_for('shows'))
 





@app.route('/artists/<artist_id>',methods= ['DELETE'])
def delete_artist(artist_id):
  error = False
  try:
    show = db.session.query(Show).filter(Show.artist_id==artist_id).delete()
    artist = db.session.query(Artist).filter(Artist.id==artist_id).delete()
    db.session.commit()
  except:
    error = True
    db.session.rollback()
  finally:
    db.session.commit()
  if  not error:
    flash('artists was sucessfully')
  else:
    flash('artist was not sucefully')
  return jsonify({
    'result' : 'true'
  })
    
@app.route('/venues/<venue_id>',methods= ['DELETE'])
def delete_venu(venue_id):
  error = False

  try: 
    show = db.session.query(Show).filter(Show.venu_id == venue_id).delete()
    venue = db.session.query(Venue).filter(Venue.id==venue_id).delete()
    
    db.session.commit()
  except:
    error = True
    db.session.rollback()
  finally:
    db.session.close()


  if not error:
      flash('Venue  successfully deleted!')
  else:
      flash('An error occurred. Venue could not be deleted.')
  
  return jsonify({
      'result': 'true' 
  })



  # on successful db insert, flash success
  # flash('Show was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

#endregion

#regionhandlers

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')
#endregion



#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
