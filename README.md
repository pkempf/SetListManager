# Setlist Manager

This is the Setlist Manager, created as a capstone project for Springboard's Computer Science Career Track program. It's available for use [here](https://setlist-mgr.herokuapp.com).

### Function

The Setlist Manager is intended for use as an aid to musicians, and in particular to musical groups, both for practice and for performances. Users can add songs to the database with information including title, artist, and optionally lyrics; those users can then organize those songs into setlists, which any user can access but which may only be edited by the users who created them. Setlists can be rearranged and edited at will. There is also a performance mode, which simplifies the interface, displays lyrics, and displays any notes users have written for the setlist being performed.

### Features

Implemented features include:

- User accounts
  - Passwords hashed and stored using bcrypt
  - Changeable usernames and passwords
  - Flexible login via either email or username
- Song database
  - Paginated list of all songs
  - Lyrics importation using [APISEEDS Lyrics API](https://apiseeds.com/documentation/lyrics)
- Setlist management
  - Drag-and-drop setlist editing using the [HTML5Sortable](https://github.com/lukasoppermann/html5sortable) library
- Simple, aesthetically pleasing user interface
  - [Bootstrap 4](https://getbootstrap.com) toolkit
  - [Flatly](https://bootswatch.com/flatly/) theme from Bootswatch
  - Optional dark mode, using [Darkly](https://bootswatch.com/darkly) theme from Bootswatch; can be enabled in user preferences
- Search functionality
  - Search by song title, artist, lyrics, setlist name, username
- Performance mode
  - Simplified and convenient user interface for use when performing a setlist

### User flow

![User flow diagram](/userflow.png)

### API used

As stated above, this project makes use of the [APISEEDS Lyrics API](https://apiseeds.com/documentation/lyrics) for importing lyrics. This is implemented via the Edit Song button, accessible from each song's specific page. The title and artist are sent as parameters to the API; if the API returns lyrics, those lyrics are set as the new lyrics of the Song object, but if no lyrics are found, the lyrics remain unchanged and an alert is shown.

### Technology stack

The Setlist Manager is built primarily in Python, using [Flask](https://flask.palletsprojects.com/en/1.1.x/), [Flask-SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com/en/2.x/), and [Flask WTForms](https://flask-wtf.readthedocs.io/en/stable/). The database used is [PostgreSQL](https://postgresql.org), and the site is hosted on [Heroku](https://heroku.com). The front end uses [Bootstrap 4](https://getbootstrap.com), [jQuery](https://jquery.com/), [HTML5Sortable](https://github.com/lukasoppermann/html5sortable), and themes from [Bootswatch](https://bootswatch.com).

### Setup

Installing and running your own instance of the Setlist Manager follows typical Flask procedures, with one exception: for full use of the lyrics import functionality, you will need to obtain a (free!) API key from [APISEEDS](https://apiseeds.com) by registering an account, then set that API key as the environment variable `LYRICS_API_KEY`.

### Planned features

Upcoming features currently include:

- Chord support, so that instrumentalists can derive greater use from the performance mode
  - Different font options; for chord support, a monotype font would almost certainly be necessary, but while I'm at it I might as well throw in a few other fonts
- Privacy settings on setlists, so that setlists can be kept private, shared only with certain users, or made fully public
- A forgotten password reset system, utilizing user email addresses

---

Thank you to [Springboard](https://springboard.com) and to Nathan Kuo, without whom I would absolutely not have been able to make this project happen.

Any and all lyrics stored on the site are used non-commercially and are the property of their respective copyright owners.
