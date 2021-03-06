from functools import wraps
from flask import request, abort, g, jsonify
import jwt
from blog.config import JWT_SECRET
from blog.database import db
from blog.models import User, Post, Comment


def require_login(func):
    @wraps(func)
    def inner(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            abort(401)
        try:
            payload = jwt.decode(token, JWT_SECRET)
        except jwt.exceptions.InvalidSignatureError:
            abort(401)
        user = db.query(User.id, User.username).filter(
            User.id == payload['user_id']).first()
        if not user:
            abort(401)
        g.user = user

        return func(*args, **kwargs)

    return inner


def owns_post(func):
    @wraps(func)
    def inner(*args, **kwargs):
        post = db.query(Post).filter(Post.id == kwargs.get('id')).first()
        if post and post.author_id != g.user.id:
            abort(403)

        return func(*args, **kwargs)

    return inner


def owns_comment(func):
    @wraps(func)
    def inner(*args, **kwargs):
        comment = db.query(Comment).filter(
            Comment.id == kwargs.get('id')).first()
        if comment and comment.author_id != g.user.id:
            abort(403)

        return func(*args, **kwargs)

    return inner
