import os
import requests

from flask import (
    Flask,
    render_template,
    request,
    flash,
    jsonify,
    redirect,
    session,
    url_for,
    g,
)
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError

from forms import (
    UserAddForm,
    UserUpdateForm,
    LoginForm,
    SongAddForm,
    SongUpdateForm,
    SetlistAddForm,
    SetlistChangeSongsForm,
    SearchForm,
)
from models import db, connect_db, User, Song, Setlist, SetlistSong

CURR_USER_KEY = "curr_user"

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URL", "postgres:///setlist-manager"
)

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = False
app.config["DEBUG_TB_INTERCEPT_REDIRECTS"] = False
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "hunter2")
toolbar = DebugToolbarExtension(app)
app.config["ITEMS_PER_PAGE"] = 20

connect_db(app)
db.create_all()

############################################################
# Error-handling


@app.errorhandler(404)
def show_404(e):
    """Shows the 404 page."""

    return render_template("404.html")


@app.errorhandler(500)
def show_500(e):
    """Shows the 500 page."""

    return render_template("500.html", error=e)


############################################################
# Sign up/sign in/log out


@app.before_request
def add_user_to_g():
    """If we're already logged in, put logged in user in Flask global (g)."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None


def do_login(user):
    """Log in."""

    session[CURR_USER_KEY] = user.id


def do_logout():
    """Log out."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]


@app.route("/sign-up", methods=["GET", "POST"])
def signup():
    """Handle signing up for the Setlist Manager."""

    form = UserAddForm()

    if form.validate_on_submit():
        try:
            user = User.signup(
                username=form.username.data,
                password=form.password.data,
                email=form.email.data,
            )
            db.session.commit()

        except IntegrityError as e:
            if "users_username_key" in repr(e):
                flash("That username is already in use.", "danger")
            elif "users_email_key" in repr(e):
                flash("That email address is already in use.", "danger")
            return render_template("sign-up.html", form=form)

        do_login(user)

        return redirect("/")

    else:
        return render_template("sign-up.html", form=form)


@app.route("/log-out", methods=["GET", "POST"])
def logout():
    """Handle logging out."""

    if request.method == "POST":
        do_logout()
        if g.user:
            flash("Successfully logged out!", "success")
        return redirect("/")
    elif not g.user:
        flash("You're already logged out.", "info")
        return redirect("/")
    else:
        return render_template("log-out.html")


@app.route("/log-in", methods=["GET", "POST"])
def login():
    """Handle logging in."""

    if g.user:
        flash("You're already logged in.", "info")
        return redirect("/")

    form = LoginForm()

    if form.validate_on_submit():
        credential = form.credential.data
        pwd = form.password.data

        user = User.authenticate_username(credential, pwd)

        if not user:
            user = User.authenticate_email(credential, pwd)

        if user:
            do_login(user)
            flash(f"Welcome back, {user.username}!", "success")
            return redirect("/")
        else:
            flash(
                "We couldn't log you in using those credentials. Please try again.",
                "danger",
            )
            return render_template("log-in.html", form=form)

    return render_template("log-in.html", form=form)

    return render_template("log-in.html")


############################################################
# Home


@app.route("/")
def show_home():
    """Shows the home page."""

    return render_template("home.html")


############################################################
# Users


@app.route("/users/<int:user_id>")
def show_user(user_id):
    """Shows a user."""

    user = User.query.get_or_404(user_id)
    return render_template("show-user.html", user=user)


@app.route("/users/update", methods=["GET", "POST"])
def update_user():
    """Updates a user."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    form = UserUpdateForm(obj=g.user)

    if form.validate_on_submit():
        user = User.authenticate_username(g.user.username, form.pwd.data)

        if user:
            if form.new_pwd.data:
                g.user.password = User.hash_password(form.new_pwd.data)

            g.user.username = form.username.data
            g.user.email = form.email.data
            g.user.darkmode = form.darkmode.data

            db.session.add(user)
            db.session.commit()
            return redirect(f"/users/{g.user.id}")

        flash(
            "We couldn't authenticate you with that password. " + "Please try again.",
            "danger",
        )
        return render_template("update-user.html", form=form)

    return render_template("update-user.html", form=form)


@app.route("/users/<int:user_id>/delete", methods=["GET", "POST"])
def del_user(user_id):
    """Deletes a user from the database."""

    if not g.user:
        flash("You must be logged in to delete a user.", "danger")
        return redirect(f"/users/{user_id}")

    user = User.query.get_or_404(user_id)
    if user_id != g.user.id:
        flash("You can't delete someone else's account.", "danger")
        return redirect(f"/users/{user_id}")

    if request.method == "POST":
        db.session.delete(user)
        db.session.commit()
        flash("User deleted successfully!", "success")
        return redirect("/")

    return render_template("/del-user.html", user=user)


@app.route("/your-setlists")
def show_my_setlists():
    """Shows the setlists of the currently logged-in user."""

    if not g.user:
        flash("You're not logged in!", "danger")
        return redirect("/")

    return render_template("your-setlists.html")


@app.route("/your-songs")
def show_my_songs():
    """Shows the songs of the currently logged-in user."""

    if not g.user:
        flash("You're not logged in!", "danger")
        return redirect("/")

    songs = Song.query.filter_by(user_id=g.user.id).order_by(Song.title.asc()).all()

    return render_template("your-songs.html", songs=songs)


############################################################
# Songs


@app.route("/songs")
def show_all_songs():
    """Shows a list of every song in the database."""

    page = request.args.get("page", 1, type=int)
    songs = Song.query.order_by(Song.title.asc()).paginate(
        page, app.config["ITEMS_PER_PAGE"], False
    )
    next_url = f"/songs?page={songs.next_num}" if songs.has_next else None
    prev_url = f"/songs?page={songs.prev_num}" if songs.has_prev else None
    return render_template(
        "all-songs.html", songs=songs.items, next_url=next_url, prev_url=prev_url
    )


@app.route("/songs/new", methods=["GET", "POST"])
def add_song():
    """Adds a song to the database."""

    form = SongAddForm()

    if form.validate_on_submit():
        title = form.title.data
        artist = form.artist.data
        lyrics = form.lyrics.data

        song = Song(user_id=g.user.id, title=title, artist=artist, lyrics=lyrics)
        db.session.add(song)
        db.session.commit()
        return redirect("/your-songs")

    return render_template("add-song.html", form=form)


@app.route("/songs/<int:song_id>")
def view_song(song_id):
    """Views a song."""

    song = Song.query.get_or_404(song_id)

    return render_template("show-song.html", song=song)


@app.route("/songs/<int:song_id>/update", methods=["GET", "POST"])
def update_song(song_id):
    """Updates a song."""

    song = Song.query.get_or_404(song_id)
    form = SongUpdateForm(obj=song)

    if form.validate_on_submit():
        new_title = form.title.data
        new_artist = form.artist.data
        new_lyrics = form.lyrics.data

        song.title = new_title
        song.artist = new_artist
        song.lyrics = new_lyrics

        db.session.add(song)
        db.session.commit()

        return redirect(f"/songs/{song_id}")

    return render_template("update-song.html", song=song, form=form)


@app.route("/songs/<int:song_id>/fetch-lyrics")
def fetch_lyrics(song_id):
    """Fetches and returns an updated song object JSON with lyrics from Genius."""

    song = Song.query.get_or_404(song_id)
    search_string = f"{song.title} {song.artist}"

    # TODO: Add API call to Genius - search > get song ID > get song

    return ""


@app.route("/songs/<int:song_id>/delete", methods=["GET", "POST"])
def del_song(song_id):
    """Deletes a song from the database."""

    if not g.user:
        flash("You must be logged in to delete a song.", "danger")
        return redirect(f"/songs/{song_id}")

    song = Song.query.get_or_404(song_id)
    if song.user_id != g.user.id:
        flash("You can't delete someone else's song.", "danger")
        return redirect(f"/songs/{song_id}")

    if request.method == "POST":
        db.session.delete(song)
        db.session.commit()
        flash("Song deleted successfully!", "success")
        return redirect("/your-songs")

    return render_template("/del-song.html", song=song)


############################################################
# Setlists


@app.route("/setlists")
def show_all_setlists():
    """Shows a list of every setlist in the database."""

    page = request.args.get("page", 1, type=int)

    setlists = Setlist.query.order_by(Setlist.name.asc()).paginate(
        page, app.config["ITEMS_PER_PAGE"], False
    )

    next_url = f"/setlists?page={setlists.next_num}" if setlists.has_next else None
    prev_url = f"/setlists?page={setlists.prev_num}" if setlists.has_prev else None

    return render_template(
        "all-setlists.html",
        setlists=setlists.items,
        next_url=next_url,
        prev_url=prev_url,
    )


@app.route("/setlists/new", methods=["GET", "POST"])
def add_setlist():
    """Adds a setlist to the database."""

    form = SetlistAddForm()

    if form.validate_on_submit():
        name = form.name.data

        setlist = Setlist(user_id=g.user.id, name=name)
        db.session.add(setlist)
        db.session.commit()
        return redirect("/your-setlists")

    return render_template("add-setlist.html", form=form)


@app.route("/setlists/<int:setlist_id>")
def show_setlist(setlist_id):
    """Shows a setlist."""

    setlist = Setlist.query.get_or_404(setlist_id)

    return render_template("show-setlist.html", setlist=setlist)


# TODO: Add update setlist functionality


@app.route("/setlists/<int:setlist_id>/edit")
def edit_setlist(setlist_id):
    """Edits the title and songs of a setlist. Uses JS/API calls."""

    setlist = Setlist.query.get_or_404(setlist_id)

    return render_template("change-setlist-songs.html", setlist=setlist)


@app.route("/setlists/<int:setlist_id>/delete", methods=["GET", "POST"])
def del_setlist(setlist_id):
    """Deletes a setlist from the database."""

    if not g.user:
        flash("You must be logged in to delete a setlist.", "danger")
        return redirect(f"/setlists/{setlist_id}")

    setlist = Setlist.query.get_or_404(setlist_id)
    if setlist.user_id != g.user.id:
        flash("You can't delete someone else's setlist.", "danger")
        return redirect(f"/setlists/{setlist_id}")

    if request.method == "POST":
        db.session.delete(setlist)
        db.session.commit()
        flash("Setlist deleted successfully!", "success")
        return redirect("/your-setlists")

    return render_template("/del-setlist.html", setlist=setlist)


@app.route("/setlists/<int:setlist_id>/perform/<int:active_song_id>")
def perform_setlist(setlist_id, active_song_id):
    """For performing from a setlist; shows songs, current song, lyrics"""

    setlist = Setlist.query.get_or_404(setlist_id)
    active_song = Song.query.get_or_404(active_song_id)

    return render_template("perform.html", setlist=setlist, active_song=active_song)


############################################################
# Misc


@app.route("/search", methods=["GET", "POST"])
def do_search():
    """Searches the database."""

    form = SearchForm()

    if form.validate_on_submit():
        category = form.category.data
        term = form.term.data

        if category == "title":
            res = Song.query.filter(Song.title.ilike(f"%{term}%")).order_by(
                Song.title.asc()
            )
            res_type = "songs"
        elif category == "artist":
            res = Song.query.filter(Song.artist.ilike(f"%{term}%")).order_by(
                Song.artist.asc()
            )
            res_type = "songs"
        elif category == "lyrics":
            res = Song.query.filter(Song.lyrics.ilike(f"%{term}%")).order_by(
                Song.title.asc()
            )
            res_type = "songs"
        elif category == "setlist":
            res = Setlist.query.filter(Setlist.name.ilike(f"%{term}%")).order_by(
                Setlist.name.asc()
            )
            res_type = "setlists"
        elif category == "user":
            res = User.query.filter(User.username.ilike(f"%{term}%")).order_by(
                User.username.asc()
            )
            res_type = "users"
        else:
            res = None
            res_type = "nothing"

        return render_template(
            "search-results.html", res=res, form=form, res_type=res_type
        )

    return render_template("search.html", form=form)


############################################################
# Internal API, for use in updating setlists


@app.route("/api/setlists/<int:setlist_id>/get-songs")
def get_songs_in_setlist(setlist_id):
    """Returns a list of the songs in and not in a setlist."""

    setlist = Setlist.query.get_or_404(setlist_id)
    setlist_songs = []

    print(setlist.songs)

    for song in setlist.songs:
        setlist_songs.append(song.serialize())

    setlist_ids = [s.id for s in setlist.songs]
    not_setlist_songs = Song.query.filter(~Song.id.in_(setlist_ids)).order_by(
        Song.title.asc()
    )

    other_songs = []

    for song in not_setlist_songs:
        other_songs.append(song.serialize())

    return jsonify(setlistSongs=setlist_songs, otherSongs=other_songs)


@app.route("/api/setlists/<int:setlist_id>/update-songs", methods=["POST"])
def update_setlist(setlist_id):
    """Updates the setlist's songs and notes."""

    setlist = Setlist.query.get_or_404(setlist_id)
    updated_song_ids = request.get_json(silent=True).get("songs")

    for setlist_song in setlist.setlist_songs:
        db.session.delete(setlist_song)

    db.session.commit()

    new_song_list = []
    new_setlist_songs_list = []

    index = 0

    for song_id in updated_song_ids:
        song = Song.query.get_or_404(song_id)
        new_song_list.append(song)
        setlist_song = SetlistSong(setlist_id=setlist_id, song_id=song_id, index=index)
        index += 1
        setlist.setlist_songs.append(setlist_song)

    serialized_songs = []
    for song in new_song_list:
        serialized_songs.append(song.serialize())

    setlist.notes = request.get_json(silent=True).get("notes")

    db.session.add(setlist)
    db.session.commit()

    return jsonify(songs=serialized_songs)
