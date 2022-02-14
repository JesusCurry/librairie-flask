from flask import Flask, jsonify, abort, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:kagami2002@localhost:5432/Librairie1'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)


class Categorie(db.Model):
    __tablename__ = 'categories'
    id_cat = db.Column(db.Integer, primary_key=True)
    libelle_cat = db.Column(db.String(80), nullable=False)
    var = db.relationship('Livre', backref='Categorie', lazy=True)

    def __init__(self, libelle_cat):
        self.libelle_cat = libelle_cat

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def format(self):
        return {
            'id_cat': self.id_cat,
            'libelle_cat': self.libelle_cat,
        }


class Livre(db.Model):
    __tablename__ = 'livres'
    id = db.Column(db.Integer, primary_key=True)
    isbn = db.Column(db.String(50), nullable=False)
    titre = db.Column(db.String(50), nullable=False)
    date_pub = db.Column(db.Date, nullable=False)
    auteur = db.Column(db.String(50), nullable=False)
    editeur = db.Column(db.String(50), nullable=False)
    id_cat = db.Column(db.Integer, db.ForeignKey('categories.id_cat'))

    def __init__(self, isbn, titre, date_pub, auteur, editeur, id_cat):
        self.isbn = isbn
        self.titre = titre
        self.date_pub = date_pub
        self.auteur = auteur
        self.editeur = editeur
        self.id_cat = id_cat

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def format(self):
        return {
            'id': self.id,
            'isbn': self.isbn,
            'titre': self.titre,
            'date_pub': self.date_pub,
            'auteur': self.auteur,
            'editeur': self.editeur,
        }


db.create_all()


################################################################
#
#            afficher la liste des livres
#
################################################################
@app.route('/livres')
def get_livres():
    livres = Livre.query.all()
    livres = [l.format() for l in livres]
    return jsonify(livres)


################################################################
#
#           afficher la liste des categories
#
################################################################
@app.route('/categories')
def get_categories():
    categories = Categorie.query.all()
    categories = [c.format() for c in categories]
    return jsonify(categories)


################################################################
#
#            rechercher un livre par son id
#
################################################################
@app.route('/livres/<int:id>')
def get_liv(id):
    livre = Livre.query.get(id)
    if livre is None:
        abort(404)
    else:
        return livre.format()


###############################################################
#
#             rechercher une categorie par son id
#
###############################################################
@app.route('/categories/<int:id_cat>')
def get_cat(id_cat):
    categorie = Categorie.query.get(id_cat)
    if categorie is None:
        abort(404)
    else:
        return categorie.format()


###############################################################
#
#                   supprimer un livre
#
###############################################################
@app.route('/livres/<int:id>', methods=['DELETE'])
def del_livr(id):
    livre = Livre.query.get(id)
    livre.delete()
    return jsonify({
        'success': True,
        'delete succefully': id,
    })


###############################################################
#
#                  supprimer une categorie
#
###############################################################
@app.route('/categories/<int:id_cat>', methods=['DELETE'])
def del_categori(id_cat):
    categorie = Livre.query.get(id_cat)
    categorie.delete()
    return jsonify({
        'success': True,
        'delete succefully': id_cat,
    })


###############################################################
#
#       afficher la liste des livres d'une categorie
#
################################################################
@app.route('/categories/<int:id_cat>/livres')
def get_categori(id_cat):
    livre = Livre.query.filter(Livre.id_cat == id_cat)
    livre = [t.format() for t in livre]
    return jsonify(livre)


################################################################
#
#               modifier le libelle de categorie
#
################################################################
@app.route('/categories/<int:id_cat>', methods=['PATCH'])
def update_categorie(id_cat):
    body = request.get_json()
    categorie = Categorie.query.get(id_cat)
    try:
        if 'libelle_cat' in body:
            categorie.libelle_cat = body['libelle_cat']
        categorie.update()
        return jsonify({
            'success modify': True,
            'categorie': categorie.format(),
        })
    except:
        abort(404)
    #################################################################


#
#              modifier les informations du livre
#
#################################################################
@app.route('/livres/<int:id>', methods=['PATCH'])
def update_livre(id):
    body = request.get_json()
    livre = Livre.query.get(id)
    try:
        if 'isbn' in body and 'titre' in body and 'auteur' in body and 'editeur' in body and 'date_pub' in body:
            livre.isbn = body['isbn']
            livre.titre = body['titre']
            livre.auteur = body['auteur']
            livre.editeur = body['editeur']
            livre.date_pub = body['date_pub']
        livre.update()
        return jsonify({
            'success modify': True,
            'livre': livre.format(),
        })
    except:
        abort(404)




