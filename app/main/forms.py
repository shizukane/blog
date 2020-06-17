from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, FileField, SubmitField
from wtforms.validators import Required

class CommentForm(FlaskForm):
    title = StringField('Comment title', validators = [Required()])
    comment = TextAreaField('Comment review')
    submit = SubmitField('Submit')

class BlogForm(FlaskForm):
    title = StringField('Post title', validators = [Required()])
    post = TextAreaField('Blog Post', validators = [Required()], render_kw={'class': 'form-control', 'rows': 20})
    submit = SubmitField('Submit')

class UpdateProfile(FlaskForm):
    bio = TextAreaField('Tell us a bit about yourself.', validators = [Required()])
    submit = SubmitField('Submit')