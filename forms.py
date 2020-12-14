from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    PasswordField,
    TextAreaField,
    BooleanField,
    SelectField,
    SelectMultipleField,
    SubmitField,
    widgets,
)
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional


class MultiCheckboxField(SelectMultipleField):
    """A wrapper for a SelectMultipleField."""

    widget = widgets.ListWidget
    option_widget = widgets.CheckboxInput()


class UserAddForm(FlaskForm):
    """Form for adding a new user."""

    username = StringField("Username", validators=[DataRequired()])
    email = StringField("Email", validators=[Email()])
    password = PasswordField("Password", validators=[Length(min=8)])
    submit = SubmitField("Add User", render_kw={"action": "post"})


class UserUpdateForm(FlaskForm):
    """Form for updating a user."""

    username = StringField("Username", validators=[DataRequired()])
    email = StringField("Email", validators=[Email()])
    darkmode = BooleanField("Use night mode")
    pwd = PasswordField(
        "Current password",
        validators=[Length(min=8, message="Please enter your current password.")],
    )
    new_pwd = PasswordField(
        label="New password (leave blank to keep current password)",
        validators=[Length(min=8), Optional()],
    )
    confirm_pwd = PasswordField(
        label="Confirm new password",
        validators=[
            Length(min=8),
            Optional(),
            EqualTo("new_pwd", "Passwords must match."),
        ],
    )
    submit = SubmitField("Update User Preferences", render_kw={"action": "post"})


class LoginForm(FlaskForm):
    """Login form."""

    credential = StringField("Username or Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[Length(min=8)])
    submit = SubmitField("Log In", render_kw={"action": "post"})


class SongAddForm(FlaskForm):
    """Form to add a song to the database."""

    title = StringField("Song title:", validators=[DataRequired()])
    artist = StringField("Artist:", validators=[DataRequired()])
    lyrics = TextAreaField("Lyrics:", validators=[Optional()])
    submit = SubmitField("Add Song", render_kw={"action": "post"})


class SongUpdateForm(FlaskForm):
    """Updates a song in the database."""

    title = StringField("Song title:", validators=[DataRequired()])
    artist = StringField("Artist:", validators=[DataRequired()])
    lyrics = TextAreaField("Lyrics:", validators=[DataRequired()])
    submit = SubmitField("Update Song", render_kw={"action": "post"})


class SetlistAddForm(FlaskForm):
    """Adds a setlist to the database."""

    name = StringField("Name:", validators=[DataRequired()])
    submit = SubmitField("Add Setlist", render_kw={"action": "post"})


class SetlistChangeSongsForm(FlaskForm):
    """Adds or removes one or more songs to/from the setlist."""

    songs = MultiCheckboxField("Songs:", coerce=int)
    submit = SubmitField("Add/Remove Songs", render_kw={"action": "post"})


class SearchForm(FlaskForm):
    """Retrieves search results based on the search term and search category."""

    category = SelectField(
        "Search category:",
        choices=[
            ("title", "Songs by title"),
            ("artist", "Songs by artist"),
            ("lyrics", "Songs by lyrics"),
            ("setlist", "Setlists by name"),
            ("user", "User by username"),
        ],
        validators=[DataRequired()],
    )
    term = StringField("Search term(s):", validators=[DataRequired()])
    submit = SubmitField("Search", render_kw={"action": "post"})
