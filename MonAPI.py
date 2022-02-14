from flask import Flask,request,jsonify,abort
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
#from flask_cors import CORS
 
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']='postgresql://postgres:kagami2002@localhost:5432/Bibliotheque'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False

daba=SQLAlchemy(app)
migrate = Migrate(app,daba)


class Categorie(daba.Model):
    __tablename__='categories'

    cat_id = daba.Column(daba.Integer,primary_key=True)
    libelle_categorie = daba.Column(daba.String(30),nullable = False)
    livres = daba.relationship('Livre',backref='categories',lazy=True)

    def __init__(self,libelle_categorie):
        self.libelle_categorie= libelle_categorie

    def insert(self):
        daba.session.add(self)
        daba.session.commit()

    def delete(self):
        daba.session.delete(self)
        daba.session.commit()

    def update(self):
        daba.session.commit()

    def format(self):
        return{
            'cat_id':self.cat_id,
            'libelle_categorie':self.libelle_categorie
        }
        

    

class Livre(daba.Model):
    __tablename__='livres'

    livre_id=daba.Column(daba.Integer,primary_key=True)
    isbn=daba.Column(daba.String(20),nullable = False)
    titre = daba.Column(daba.String(200),nullable = False)
    date_publication = daba.Column(daba.String(20),nullable = False)
    auteur = daba.Column(daba.String(200),nullable = False)
    editeur = daba.Column(daba.String(200),nullable = False)
    categorie_id = daba.Column(daba.Integer,daba.ForeignKey("categories.cat_id"), nullable= False)

    def __init__(self,isbn,titre,date_publication,auteur,editeur,cat_id):
        self.isbn = isbn
        self.titre = titre
        self.date_publication = date_publication
        self.auteur = auteur
        self.editeur= editeur
        self.cat_id = cat_id

    def insert(self):
        daba.session.add(self)
        daba.session.commit()
    
    def delete(self):
        daba.session.delete(self)
        daba.session.commit()

    def update(self):
        daba.session.commit()

    def format(self):
        return{
            'id':self.livre_id,
            'isbn':self.isbn,
            'titre':self.titre,
            'date_publication':self.date_publication,
            'auteur':self.auteur,
            'editeur':self.editeur,
            'cat_id':self.categorie_id
        }

daba.create_all()




#-------------------------------------------------------
#Fonction permettant d'afficher les éléments d'une liste
#-------------------------------------------------------

def page(request):
    REQ = [l.format() for l in request]
    return REQ


#----------------------------------------------------------
#Fonction permettant d'afficher la liste de tous les livres
#----------------------------------------------------------


@app.after_request
def after_request(answer):
    answer.headers.add('Access-Control-Allow-Headers','Content-Type,Authorization,true')
    answer.headers.add('Access-Control-Allow-Methods','GET,PUT,POST,DELETE,OPTIONS')
    return answer


@app.route('/livres')
def get_livres():
    try:
        livres= Livre.query.all()
        livres = page(livres)
        return jsonify({
            'success':True,
            'status_code':200, 
            'livres':livres,
            'total_livres':len(livres) 
        })
    except:
        abort(400)
    finally:
        daba.session.close()

    
#---------------------------------------------
#chercher un livre ne particulier avec son id
#---------------------------------------------
@app.route('/livres/<int:id>')
def get_livre(id):
    livre = Livre.query.get(id)
    if livre is None:
        abort(404)
    else:
        return livre.format()


#-------------------------------------------
#Lister la liste des livres d'une categorie
#-------------------------------------------
@app.route('/categories/<int:id>/livres')
def livre_categorie(id):
    try:
        categories= Categorie.query.get(id)
        livres = Livre.query.filter_by(livre_id=id).all()
        livres = page(livres)
        return jsonify({
            'success':True,
            'status_code':200,
            'total':len(livres),
            'type':categories.format(),
            'livres':livres
        })
    except:
        abort(404)
    finally:
        daba.session.close()

    
#------------------------------------------
#lister toutes les categories
#------------------------------------------
@app.route('/categories')
def get_categories():
    categories = Categorie.query.all()
    categories = page(categories)
    if categories is None:
        abort(404)
    else:
        return jsonify({
            'success':True,
            'status_code':200,
            'total':len(categories),
            'categorie':categories

        })

    
#---------------------------------------
#chercher une categorie par son id
#---------------------------------------
@app.route('/categories/<int:id>')
def get_categorie(id):
    categorie = Categorie.query.get(id)
    if categorie is None:
        abort(404)
    else:
        return categorie.format()


#--------------------------------------
#supprimer un livre
#--------------------------------------
@app.route('/livres/<int:id>',methods = ['DELETE'])
def supp_livre(id):
    try:
        livre = Livre.query.get(id)
        livre.delete()
        return jsonify({
            'success':True,
            'livre_id':id,
            'total_rest':Livre.query.count()
        })
    except:
        abort(404)
    finally:
        daba.session.close()

    

#--------------------------------------
#supprimer une categorie
#--------------------------------------
@app.route('/categories/<int:id>',methods=['DELETE'])
def supp_cat(id):
    try:
        categorie = Categorie.query.get(id)
        categorie.delete()
        return jsonify({
            'success':True,
            'id_cat':id,
            'categories_rest':Categorie.query.count()
        })
    except:
        abort(404)
    finally:
        daba.session.close()



#-------------------------------------
#modifier les informations d'un livre
#-------------------------------------
@app.route('/livres/<int:id>',methods=['PATCH'])
def modif_livre(id):
    body = request.get_json()
    livre = Livre.query.get(id)
    try:
        if 'titre'in body and 'auteur'in body and'editeur' in body:
            livre.titre=body['titre']
            livre.auteur= body['auteur']
            livre.editeur= body['editeur']
            livre.update()
            return livre.format()
    except:
            abort(404)



#----------------------------------
#modifier le libelle d'une categorie
#----------------------------------
@app.route('/categories/<int:id>',methods=['PATCH'])
def modif_libcate(id):
    body = request.get_json()
    categorie = Categorie.query.get(id)
    try:
        if 'libelle_categorie'in body:
            categorie.libelle_categorie = body['libelle_categorie']
        categorie.update()
        return categorie.format()
    except:
        abort(404)

#-----------------------------------------------   
#Rechercher un livre par son titre ou son auteur
#-----------------------------------------------
@app.route('/livres/<string:word>')
def rech_livre(word):
    sentence = '%'+word+'%'
    titre = Livre.query.filter(Livre.titre.like(sentence)).all()
    titre = page(titre)
    return jsonify ({
        'livres':titre
    })

@app.route('/categories',methods=['POST'])
def ajout_cat():
    body = request.get_json()
    nouv_categorie = body['libelle_categorie = new_categorie']
    categorie= Categorie(libelle_categorie=nouv_categorie)
    categorie.insert()
    return jsonify({
        'success':True,
        'added':categorie.format(),
        'categories':Categorie.query.count()
    })

@app.route('/livres',methods=['POST'])
def ajout_livre():
    body = request.get_json()
    isbn = body['isbn']
    nouv_titre=body['titre']
    nouv_date = body['date_publication']
    nouv_auteur = body['auteur']
    nouv_editeur = body['editeur']
    cat_id = body['cat_id']
    livre = Livre(isbn=isbn,titre=nouv_titre,date_publication=nouv_date,auteur=nouv_auteur,editeur=nouv_editeur,
    cat_id=cat_id)

    livre.insert()

    count = Livre.query.count()
    return jsonify({
        'success':True,
        'ajouter':livre.format(),
        'total_livres':count
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success':False,
        'error':404,
        'message':"indisponibilité"
    }),404









