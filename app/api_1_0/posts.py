from . import api
from .authentication import auth
from .errors import unauthorized, bad_request, forbidden, validation_error
from flask import jsonify, request, current_app, url_for
from ..models import Post, User, Permission, Comment
from ..decorators import permission_required
from .errors import unauthorized, bad_request, forbidden, validation_error

@api.route('/posts/')
@auth.login_required
def get_posts():
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
    posts = pagination.items
    rev = None
    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_posts', page=page-1, _external=True)
    next = None
    if pagination.has_next:
        next = url_for('api.get_posts', page=page+1, _external=True)
    return jsonify({
        'posts': [post.to_json() for post in posts],
        'prev': prev,
        'next': next,
        'count': pagination.total
    })
    return jsonify({ 'posts': [post.to_json() for post in posts] })

@api.route('/posts/<int:id>')
@auth.login_required
def get_post(id):
    post = Post.query.get_or_404(id)
    return jsonify(post.to_json())

@api.route('/get_user/<int:id>')
@auth.login_required
def get_user(id):
    user = User.query.get_or_404(id)
    return jsonify(user.to_json())

@api.route('/get_user_posts/<int:id>')
@auth.login_required
def get_user_posts(id):
    posts = Post.query.filter_by(author_id=id).all()
    return jsonify({ 'posts': [post.to_json() for post in posts] })

@api.route('/get_user_followed_posts/<int:id>')
@auth.login_required
def get_user_followed_posts(id):
    posts = Post.query.filter_by(author_id=id).all()
    return jsonify({ 'posts': [post.to_json() for post in posts] })

@api.route('/get_post_comments/<int:id>')
@auth.login_required
def get_post_comments(id):
    comments = Comment.query.filter_by(post_id=id).all()
    return jsonify({ 'comments': [comment.to_json() for comment in comments] })

@api.route('/posts/', methods=['POST'])
@permission_required(Permission.WRITE_ARTICLES)
def new_post():
    post = Post.from_json(request.json)
    post.author = g.current_user
    db.session.add(post)
    db.session.commit()
    return jsonify(post.to_json()), 201,\
           {'Location': url_for('api.get_post', id=post.id, _external=True)}

@api.route('/posts/<int:id>', methods=['PUT'])
@permission_required(Permission.WRITE_ARTICLES)
def edit_post(id):
    post = Post.query.get_or_404(id)
    if g.current_user != post.author and not g.current_user.can(Permission.ADMINISTER):
        return forbidden('Insufficient permissions')
    post.body = request.json.get('body', post.body)
    db.session.add(post)
    return jsonify(post.to_json())