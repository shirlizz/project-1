#Web Programming course
#Author : Elias Guaman / mail : cruz.guaman@yachaytech.edu.ec
#Tutor : Rigoberto Fonseca
#Date: Nov/2019


from flask import Flask, render_template, redirect, url_for, request, jsonify, abort,flash,session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from forms import LoginForm, PostForm, SignupForm
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse

app=Flask(__name__)
app.config.update(
  ENV='developmet',
  SECRET_KEY='secret',
  DEBUG=True,
  SQLALCHEMY_DATABASE_URI= "postgres://hlcellsnmwzcnm:de87153f5c3f0358ec5f0e8ae8b21468e0ecaa2e8b40f906e8a5bae3e1ca3b54@ec2-174-129-253-146.compute-1.amazonaws.com:5432/d6nem5fv43fj8u",
)
login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.init_app(app)
db=SQLAlchemy(app)

##=============================================================================
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import IntegrityError
class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(256), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    def __repr__(self):
        return '<User {self.email}>'
        # return f'{self.id}'
    def set_password(self, password):
        self.password = generate_password_hash(password)
    def check_password(self, password):
        return check_password_hash(self.password, password)
    def save(self):
        if not self.id:
            db.session.add(self)
        db.session.commit()
    @staticmethod
    def get_by_id(id):
        return User.query.get(id)
    @staticmethod
    def get_by_email(email):
        return User.query.filter_by(email=email).first()
#=======================

@app.route('/')
def index():
  return render_template('index.html')

@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(int(user_id))

@app.route("/api/book/", methods=['GET', 'POST'], defaults={'book_id': 1})
@app.route("/api/book/<string:book_id>/", methods=['GET', 'POST'])
@login_required
def book_form(book_id):
    if book_id is None:
        return "Nada que presentar"
    sql=text("select b.*, count(id_book), case when count(rating)=0 then 0 else round(avg(rating)) end from books as b full outer join user_book on b.id=id_book where b.isbn=:id group by b.id").params(id=book_id)
    rs=db.engine.execute(sql).fetchone()
    if rs is None:
        abort(404)
    return jsonify({"ISBN":rs[1],"Title":rs[2],"Author":rs[3], "Year":rs[4],"count_review":rs[5],"avg_rating":float(rs[6])})

@app.route('/list', methods=['GET', 'POST'])
def listar():
    sr=request.form['busqueda']
    prm=request.form['search_param']

    if not sr:
        flash("Ingrese una busqueda")
        return render_template('book_page.html', datos=None, prm=prm)
    if prm=="title":
        sql = text("select * from books where lower(title) like lower(:name)").params({'name':"%"+sr+"%"})
    elif prm=="author":
        sql = text("select * from books where lower(author) like lower(:name)").params({'name':"%"+sr+"%"})
    else:
        sql = text("select * from books where lower(isbn) like lower(:name)").params({'name':"%"+sr+"%"})
    
    query=db.engine.execute(sql).fetchall()

    if not query:
        flash("No found!")
        return render_template('book_page.html', datos=None, prm=prm)
    flash("Resultados encontrados: "+str(len(query)))
    return render_template('book_page.html', datos=enumerate(query), prm=prm)

@app.route('/details/<int:dato>')
def details(dato):
    do_review=False
    sql = text("select * from books where id=:name").params(name=dato)
    query=db.engine.execute(sql).fetchall()
    sql = text("select * from user_book where id_user=:user and id_book=:name").params(user=session['user_id'],name=dato)
    query1=db.engine.execute(sql).fetchall()
    [print(row) for row in query1]
    if not query1:
        do_review=True
        print("Hacer Review")
    return render_template('book_details.html', do_review=do_review, datos2=query1, idb=dato, isbn=query[0])

@app.route('/review/<int:idb>', methods=['GET','POST'])
def review(idb):
    if request.method=='POST':
        print("================ post review")
        calificacion = request.form['calificacion']
        opinion=request.form['opinion']
        print(calificacion, opinion, idb)
        sql = text("insert into user_book (id_user, id_book, rating, opinion) values(:idu,:idb,:rt,:op)").params(idu=session['user_id'],idb=idb,rt=calificacion,op=opinion)
        db.engine.execute(sql)
        return redirect(url_for('book_page'))
    return render_template('review.html', dato=idb)

@app.route('/book_page')
@login_required
def book_page():
    return render_template('book_page.html',prm='title')

@app.route('/login', methods=['GET', 'POST'])
def login():
  form = LoginForm()
  print("===========LoginForm=======")
  if form.validate_on_submit():
    user = User.get_by_email(form.email.data)
    print("==================")
    print(session)
    if user is not None and user.check_password(form.password.data):
      print("=========Logeado Correcto")
      login_user(user, remember=form.remember_me.data)
      next_page = request.args.get('next')
      if not next_page or url_parse(next_page).netloc != '':
          print("=========url_parse")
          next_page = url_for('book_page')
      print(session)
      return redirect(next_page)
    return redirect(url_for('index'))
  return render_template('login.html',form=form)

@app.route('/register', methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = SignupForm()
    error = None
    if form.validate_on_submit():
        print("validate submit")
        username = form.username.data
        email = form.email.data
        password = form.password.data
        # Comprobamos que no hay ya un usuario con ese email
        user = User.get_by_email(email)
        print(user)
        if user is not None:
            error = f'El email {email} ya está siendo utilizado por otro usuario'
        else:
            # Creamos el usuario y lo guardamos
            user = User(username=username, email=email)
            user.set_password(password)
            user.save()
            # Dejamos al usuario logueado
            login_user(user, remember=True)
            next_page = request.args.get('next', None)
            if not next_page or url_parse(next_page).netloc != '':
                next_page = url_for('index')
            return redirect(next_page)
    return render_template("register.html", form=form, error=error)
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

if __name__ == "__main__":
  app.run()
