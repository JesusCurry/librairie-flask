from flask import Flask, render_template, jsonify, request
from flask_sqlalchemy import SQLAlchemy
import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] ='postgresql://postgres:kagami2002@localhost:5432/Librairie'

db = SQLAlchemy(app)


@app.route('/')
def index():
    return '<h2>welcome to flask journey</h2>'


@app.route('/Livres/', methods=['GET'])
def get_books():
    d = {}
    l = list()
    x = 0
    query = Livre.query.all()
    for livre in query:
        l.append({'id': livre.id, 'isbn': livre.isbn, 'titre': livre.titre, 'datePublication': livre.datePublication,
                  'categorie_id': livre.categorie_id, 'auteur': livre.auteur, 'editeur': livre.editeur})
        x = x + 1
    d["succes"] = "OK"
    d["livres"] = l
    return d


@app.route('/Categories/', methods=['GET'])
def get_categories():
    d = {}
    l = list()
    x = 0
    query = Categorie.query.all()
    for c in query:
        l.append({'id': c.id, 'libelle': c.libelle_categorie})
    d["succes"] = "OK"
    d["categories"] = l
    return d


@app.route('/Livres/<int:id>')
def get_livre(id):
    livre = Livre.query.all()
    for i in livre:
        if i.id == id:
            return ({"livre": {"id": i.id, "isbn": i.isbn, "titre": i.titre, "datePublication": i.datePublication,
                               "categorie_id": i.categorie_id, "auteur": i.auteur, "editeur": i.editeur},
                     "message": "Trouvé", "succes": "OK"})

    return ({"message": "Non Trouvé", "succes": " NOT OK"})


@app.route('/Livres/<int:id>', methods=['DELETE'])
def delete_livre(id):
    try:
        i = Livre.query.filter_by(id=id)
        b = i[0]
        i.delete()
        db.session.commit()
        return ({"livre": {"id": b.id, "isbn": b.isbn, "titre": b.titre, "datePublication": b.datePublication,
                           "categorie_id": b.categorie_id, "auteur": b.auteur, "editeur": b.editeur},
                 "success": "OK", "deleted": "True"})
    except Exception as e:
        print(e)
        pass
    return ({"message": "L'id n'existe pas", "succes": "NOT OK", "deleted": "False"})


@app.route('/LivresUpdate/', methods=['PUT'])
def update_livre():
    try:
        b_d = json.loads(request.data.decode())
        c = Livre.query.filter_by(id=b_d["id"])
        if c == None or c.count() == 0:
            return ({"success": "False", "Erreur": "L'id du livre n'existe pas"})

        for key in b_d:
            Livre.query.filter_by(id=b_d['id']).update({key: b_d[key]})
        db.session.commit()
        return ({"success": "OK", "Message": "Livre mis à jour"})
    except:
        return ({"message": "Une erreur est survenue"})


@app.route('/Categorie/<int:id>')
def get_categorie(id):
    categorie = Categorie.query.all()
    for c in categorie:
        if c.id == id:
            return ({"succes": "OK", "categorie": {"id": c.id, "libelle_categorie": c.libelle_categorie}})
    return ({"message": "Non Touvé", "succes": " NOT OK"})


@app.route('/Categorie/<int:id>', methods=['DELETE'])
def delete_categorie(id):
    try:
        c = Categorie.query.filter_by(id=id)
        d = c[0]
        c.delete()
        db.session.commit()
        return ({"Categorie": {"id": d.id, "libelle_categorie": d.libelle_categorie}, "deleted": "True", "success": " OK"})
    except Exception as ex:
        print(ex)
        return ({"deleted": "False", "success": "NOT OK"})


@app.route('/CategorieUpdate/', methods=['PUT'])
def update_categorie():
    b_d = json.loads(request.data.decode())
    c = Categorie.query.filter_by(id=b_d["id"])
    if c == None or c.count() == 0:
        return ({"success": "False", "Erreur": "L'id n'existe pas"})
    for key in b_d:
        Categorie.query.filter_by(id=b_d['id']).update({key: b_d[key]})
    db.session.commit()
    return ({"success": "True", "Message": "Categorie mise à jour"})


@app.route('/Categorie/<int:id>/Livres/')
def get_categorie_livre(id):
    d = {}
    li = list()
    # categorie = Categorie.query.all()
    livre = Livre.query.all()
    for i in livre:
        if id == i.categorie_id:
            li.append({"id": i.id, "code": i.code, "titre": i.titre, "datePublication": i.datePublication,
                       "categorie_id": i.categorie_id, "auteur": i.auteur, "editeur": i.editeur})
    d["categorie"] = id
    d["livres"] = li
    d["success"] = "OK"
    return d


# return ({"message":"Not Found"})


@app.route('/ajouter/Livres/', methods=['POST'])
def get_livrex():
    book_data = json.loads(request.data.decode())
    livrex = Livre(isbn=book_data['isbn'], titre=book_data['titre'], datePublication=book_data['datePublication'],
                   categorie_id=book_data['categorie_id'], auteur=book_data['auteur'],
                   editeur=book_data['editeur'])

    db.session.add(livrex)
    db.session.commit()
    return {"message" : "Livre ajouté"}


@app.route('/ajouter/Categorie', methods=['POST'])
def ajouter_categorie():
    categorie_data = json.loads(request.data.decode())
    categorie = Categorie(id=categorie_data["id"], libelle_categorie=categorie_data["libelle_categorie"])
    db.session.add(categorie)
    db.session.commit()
    return {"message": "Categorie ajoutée"}


class Categorie(db.Model):
    __tablename__ = 'Categories'
    id = db.Column(db.Integer, primary_key=True)
    libelle_categorie = db.Column(db.String(100), nullable=False)
    livre = db.relationship("Livres", backref="Categories", lazy=True)


# db.create_all()

class Livre(db.Model):
    __tablename__ = 'Livres'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    isbn = db.Column(db.String(50), nullable=False)
    titre = db.Column(db.String(200), nullable=False)
    datePublication = db.Column(db.Date, nullable=False)
    categorie_id = db.Column(db.Integer, db.ForeignKey('Categories.id'), nullable=False)
    auteur = db.Column(db.String(200), nullable=False)
    editeur = db.Column(db.String(200), nullable=False)


db.create_all()
# s Livre(db.Model):
# app.run(debug=True)
