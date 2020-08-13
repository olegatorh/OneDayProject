from app import app
from flask import render_template, redirect, url_for, flash, request
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Post, Borda
from app import db
from app.forms import RegistrationForm, LoginForm, PostForm, BoardForm
from werkzeug.urls import url_parse


@app.route('/', methods=['GET', 'POST'])
def index():
    all_boards = Borda.query.order_by(Borda.timestamp.desc())
    form = BoardForm()
    if form.validate_on_submit():
        if form.validate_board(form.bord_name) is True:
            flash(f"sorry, but {form.bord_name.data} already exists")
            return redirect(url_for('index'))
        new_bord = Borda(bord_name=form.bord_name.data, creator_name=current_user.username)
        db.session.add(new_bord)
        db.session.commit()
        return redirect(f'/{form.bord_name.data}')
    return render_template("index.html", title="Borda",  all_boards=all_boards, form=form)


@app.route('/<bord_name>', methods=['GET', 'POST'])
def bord_page(bord_name):
    form = BoardForm()
    form_board = PostForm()
    all_boards = Borda.query.order_by(Borda.timestamp.desc())
    page = request.args.get('page', 1, type=int)
    posts_on_page = Post.query.order_by(Post.timestamp.desc()).filter_by(bord_id=bord_name).paginate(page,
                      app.config['POSTS_PER_PAGE'], False)
    borda = Borda.query.filter_by(bord_name=bord_name).first()
    next_url = url_for("bord_page", bord_name=bord_name,
                       page=posts_on_page.next_num) if posts_on_page.has_next else None
    prev_url = url_for("bord_page", bord_name=bord_name,
                       page=posts_on_page.prev_num) if posts_on_page.has_prev else None
    if form_board.validate_on_submit():
        post_content = form_board.postBody.data
        new_post = Post(body=post_content, author=current_user.username, bord_id=bord_name)
        db.session.add(new_post)
        db.session.commit()
        return redirect(f"/{bord_name}")
    return render_template('bordPage.html', borda=borda, posts=posts_on_page.items, bord_name=bord_name,
                           form=form, form_board=form_board, all_boards=all_boards,
                           next_url=next_url, prev_url=prev_url, title=bord_name
                           )


@app.route('/boards/delete/<int:id>')
def delete_boards(id):
    board_name = Borda.query.get_or_404(id)
    all_post = Post.query.filter_by(bord_id=board_name.bord_name).all()
    db.session.delete(board_name)
    db.session.commit()
    for posts in all_post:
        db.session.delete(posts)
        db.session.commit()
    return redirect("/")


@app.route('/posts/delete/<int:id>')
def delete(id):
    post = Post.query.get_or_404(id)
    board_name = Post.query.filter_by(id=id).first()
    db.session.delete(post)
    db.session.commit()
    return redirect(f"/{board_name.bord_id}")


@app.route('/posts/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    post = Post.query.get_or_404(id)
    board_name = Post.query.filter_by(id=id).first()
    flash("your post has been edited")
    if request.method == 'POST':
        post.body = request.form['content']
        db.session.commit()
        return redirect(f"/{board_name.bord_id}")
    else:
        return render_template('edit.html', post=post, title="EDIT")


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='registration', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))



