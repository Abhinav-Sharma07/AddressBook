from flask import Flask ,render_template, request, redirect,url_for
from flask_sqlalchemy import SQLAlchemy
import math
import pandas as pd
from io import BytesIO
from flask import send_file

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

# Route to download existing data
@app.route('/download_update_template')
def download_update_template():
    contacts = Contact.query.all()
    data = [{
        'ID': c.id,
        'Name': c.name,
        'Father Name': c.fathername,
        'Father Mobile': c.fathermobile,
        'Father Email': c.fatheremail,
        'Mother Name': c.mothername,
        'Mother Mobile': c.mothermobile,
        'Mother Email': c.motheremail,
        'Address': c.address
    } for c in contacts]

    df = pd.DataFrame(data)
    output = BytesIO()
    df.to_excel(output, index=False)
    output.seek(0)
    return send_file(output, download_name="contacts_to_update.xlsx", as_attachment=True)

# Route to import new students
@app.route('/import_new_students', methods=['POST'])
def import_new_students():
    file = request.files['file']
    if file.filename.endswith('.xlsx'):
        df = pd.read_excel(file)
        for _, row in df.iterrows():
            contact = Contact(
                name=row['Name'],
                fathername=row['Father Name'],
                fathermobile=row['Father Mobile'],
                fatheremail=row['Father Email'],
                mothername=row['Mother Name'],
                mothermobile=row['Mother Mobile'],
                motheremail=row['Mother Email'],
                address=row['Address']
            )
            db.session.add(contact)
        db.session.commit()
    return redirect(url_for('index'))

# Route to upload and update existing students by ID
@app.route('/upload_updated_excel', methods=['POST'])
def upload_updated_excel():
    file = request.files['file']
    if file.filename.endswith('.xlsx'):
        df = pd.read_excel(file)
        for _, row in df.iterrows():
            contact = Contact.query.get(int(row['ID']))
            if contact:
                contact.name = row['Name']
                contact.fathername = row['Father Name']
                contact.fathermobile = row['Father Mobile']
                contact.fatheremail = row['Father Email']
                contact.mothername = row['Mother Name']
                contact.mothermobile = row['Mother Mobile']
                contact.motheremail = row['Mother Email']
                contact.address = row['Address']
        db.session.commit()
    return redirect(url_for('index'))

if __name__=='__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
