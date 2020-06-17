from flask import render_template, request, redirect, url_for, abort
from ..request import get_quote
from . import main
from ..models import User, Blog, Subscriber, Comment
from .forms import BlogForm, CommentForm, UpdateProfile
from flask_login import login_required, current_user
from .. import db, photos
from ..email import mail_message

@main.route('/')
def index():

    '''
    View root page function that returns the index page and its data
    '''
    title = 'Jabulani - There\'s a story in everything'
    quote = get_quote()
    blogs = Blog.query.all()
    return render_template('index.html', title=title, quote=quote, blogs = blogs)

@main.route('/user/<uname>')
def profile(uname):
    user = User.query.filter_by(username = uname).first()
    blogs = Blog.query.filter_by(user_id = user.id).order_by(Blog.posted.desc())

    if user is None:
        abort(404)

    return render_template("profile/profile.html", user = user, blogs = blogs)

@main.route('/user/<uname>/delete/<blog_id>')
@login_required
def del_blog(uname, blog_id):
    user = User.query.filter_by(username = uname).first()
    blogs = Blog.query.filter_by(user_id = user.id).order_by(Blog.posted.desc())
    blog = Blog.query.filter_by(id = blog_id).first()

    if blog.user_id == current_user.id:
        blog.delete_blog()

    return render_template("profile/profile.html", user = user, blogs = blogs)

@main.route('/user/<uname>/update',methods = ['GET','POST'])
@login_required
def update_profile(uname):
    user = User.query.filter_by(username = uname).first()
    if user is None:
        abort(404)

    form = UpdateProfile()

    if form.validate_on_submit():
        user.bio = form.bio.data

        db.session.add(user)
        db.session.commit()

        return redirect(url_for('.profile',uname=user.username))

    return render_template('profile/update.html',form =form,user=user)

@main.route('/user/<uname>/update/pic',methods= ['POST'])
@login_required
def update_pic(uname):
    user = User.query.filter_by(username = uname).first()
    if 'photo' in request.files:
        filename = photos.save(request.files['photo'])
        path = f'photos/{filename}'
        user.profile_pic_path = path
        db.session.commit()
    return redirect(url_for('main.profile',uname=uname))

@main.route('/user/<uname>/blog',methods= ['GET','POST'])
@login_required
def new_blog(uname):
    user = User.query.filter_by(username = uname).first()
    if user is None:
        abort(404)

    form = BlogForm()
    blog = Blog()

    if form.validate_on_submit():
        blog.title = form.title.data
        blog.message = form.post.data
        blog.user_id = current_user.id


        db.session.add(blog)
        db.session.commit()

        subscribers = Subscriber.query.all()
        for subscriber in subscribers:
            mail_message("New Blog Post", "email/welcome_user", subscriber.email, user = subscriber)

        return redirect(url_for('.profile',uname=user.username))

    return render_template('new_blogpost.html',uname=uname, user = user, BlogForm = form)

@main.route('/comments/<blog_id>')
@login_required
def comments(blog_id):
    blog = Blog.query.filter_by(id = blog_id).first()
    comments = Comment.query.filter_by(blog_id = blog.id).order_by(Comment.posted.desc())


    return render_template('comments.html', blog = blog, comments = comments)

@main.route('/comment/delete/<blog_id>/<comment_id>')
@login_required
def del_comment(blog_id, comment_id):
    blog = Blog.query.filter_by(id = blog_id).first()
    comments = Comment.query.filter_by(blog_id = blog.id).order_by(Comment.posted.desc())
    comment = Comment.query.filter_by(id = comment_id).first()
    if blog.user_id == current_user.id or comment.user_id == current_user.id:

        Comment.delete_comment(comment)

    return render_template('comments.html', blog = blog, comments = comments)

@main.route('/blog/comment/new/<blog_id>', methods = ['GET', 'POST'])
@login_required
def new_review(blog_id):
    form = CommentForm()
    blog = Blog.query.filter_by(id = blog_id).first()
    comment = Comment()

    if form.validate_on_submit():
        comment.title = form.title.data
        comment.comment = form.comment.data
        comment.blog_id = blog_id
        comment.user_id = current_user.id

        db.session.add(comment)
        db.session.commit()

        return redirect(url_for('main.comments', blog_id=blog.id ))

    return render_template('new_comment.html', comment_form = form)