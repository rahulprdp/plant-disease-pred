
from email.policy import default
import pickle
from flask import Flask, render_template , request,redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from fileinput import filename
import sqlalchemy


#ML Code 

import tensorflow as tf
import os
import cv2
import numpy as np

model =tf.keras.models.load_model(os.path.join('models','model2.h5'))

def predict(name):
    img = cv2.imread(name)
    resize = tf.image.resize(img,(256,256))
    yhat = model.predict(np.expand_dims(resize/255,0))
    return yhat

## End of ML Code


##Flask App -------------------------------------------------------
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///subs.db'

#Initialise DB
db=SQLAlchemy(app)

#Creating Models

class sub(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    mail = db.Column(db.String(200), nullable=False)
    dateCreated = db.Column(db.DateTime, default=datetime.utcnow)

    #Create fun to return string when we add stuff
    def __repr__(self):
        return '<name %r>' % self.id



@app.route('/')
def index() :
    return render_template("index.html")

@app.route('/success', methods = ['POST'])  
def success():  
    f = request.files['file']
    f.save(f.filename)  
    filenm = predict(f.filename)
    os.remove(f.filename)

    if(filenm[0][0] == 1):
        res = "Unhealthy"
    else:
        res = "Healthy"
    return render_template("index.html", filenm = filenm[0][0])  


@app.route('/about')
def about() :
    return render_template("about.html")



@app.route('/appends', methods=['POST','GET'])
def appends():
    fname = request.form.get('name')
    fmail = request.form.get("userEmail")

    
    if request.method=="POST":
        if not fname or not fmail :
            errorStmt = "All Fields are required"
            return render_template("about.html",errorStmt=errorStmt, name=fname, mail=fmail)


        new_sub = sub(name=fname,mail=fmail)
        try:
            db.session.add(new_sub)
            db.session.commit()
            return redirect('/appends')
        except :
            return "<h1> There Was An Error </h1>"

    else :
        subs = sub.query.order_by(sub.dateCreated)
        n=""
        for s in subs:
            n=s.name
            
        return render_template("about.html",name="", mail="", sucMsg=n + " Was Scuccessfull Added ! ")


@app.route('/ctrl', methods=['POST','GET'])
def cntrl():
    subs = sub.query.order_by(sub.dateCreated)
    return render_template("ctrl.html",ss=subs)


