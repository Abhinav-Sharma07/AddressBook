from flask import Flask ,render_template, request, redirect,url_for
from flask_sqlalchemy import SQLAlchemy
import math

app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///Data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db=SQLAlchemy(app)

class Contact (db.Model):
    id=db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String(100))
    fathername=db.Column(db.String(100))
    fathermobile=db.Column(db.String(20))
    fatheremail=db.Column(db.String(200))
    mothername=db.Column(db.String(100))
    mothermobile=db.Column(db.String(20))
    motheremail=db.Column(db.String(200))
    address=db.Column(db.String(200))

@app.route('/')
def index():
    search_query = request.args.get('q','')
    page = request.args.get('page',1, type=int)
    per_page = 10

    if search_query :
        contacts = Contact.query.filter(
            Contact.name.contains(search_query)|
            Contact.fathermobile.contains(search_query)|
            Contact.fatheremail.contains(search_query)|
            Contact.mothermobile.contains(search_query)|
            Contact.motheremail.contains(search_query)|
            Contact.mothername.contains(search_query)|
            Contact.fathername.contains(search_query)
            
        )
    else:
        contacts = Contact.query

    total=contacts.count()
    contacts_paginated = contacts.paginate(page=page, per_page=per_page)
    return render_template('index.html', contacts=contacts_paginated, query=search_query,total_pages=math.ceil(total / per_page))
                           
@app.route('/add',methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        contact = Contact(
            name=request.form['name'],
            fathermobile=request.form['fathermobile'],
            mothermobile=request.form['mothermobile'],
            fathername=request.form['fathername'],
            mothername=request.form['mothername'] ,
            fatheremail=request.form['fatheremail'],
            motheremail= request.form['motheremail'],
            address=request.form['address']  
        )
        db.session.add(contact)
        db.session.commit()
        return redirect (url_for('index'))
    return render_template('form.html',action='add', contact=None)
@app.route('/edit/<int:id>',methods=['GET','POST'])

def edit(id):
    contact=Contact.query.get_or_404(id)
    if request.method == 'POST':
        contact.name=request.form['name']
        contact.fathermobile=request.form['fathermobile']
        contact.mothermobile=request.form['mothermobile']
        contact.fathername=request.form['fathername']
        contact.mothername=request.form['mothername'] 
        contact.address=request.form['address']
        contact.motheremail=request.form['motheremail']
        contact.fatheremail=request.form['fatheremail']
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('form.html',action='Edit',contact=contact)

@app.route ('/delete/<int:id>')
def delete (id):
    contact=Contact.query.get_or_404(id)
    db.session.delete(contact)
    db.session.commit()
    return redirect(url_for('index'))

if __name__=='__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
