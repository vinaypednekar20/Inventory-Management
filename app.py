from flask import Flask,render_template,url_for,redirect,request,flash,make_response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func,or_
from datetime import datetime,date
import pdfkit
config = pdfkit.configuration(wkhtmltopdf='C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe')

app = Flask('__name__')

app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///inventory.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["SECRET_KEY"]="SECRETKEY_TEST"
db = SQLAlchemy(app)


class Product(db.Model):
	id = db.Column(db.Integer,primary_key=True)
	name = db.Column(db.String(100),nullable=False)
	date_created = db.Column(db.DateTime, default=datetime.utcnow)
	date_updated = db.Column(db.DateTime, default=datetime.utcnow)
	def __repr__(self):
		return 'Product'+str(self.id)

class Location(db.Model):
	id = db.Column(db.Integer,primary_key=True)
	name = db.Column(db.String(100),nullable=False)
	date_created = db.Column(db.DateTime, default=datetime.utcnow)
	date_updated = db.Column(db.DateTime, default=datetime.utcnow)
	def __repr__(self):
		return 'Location'+str(self.id)
class ProductMovement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    from_location = db.Column(db.String(100))
    to_location = db.Column(db.String(100))
    product_id = db.Column(db.Integer, nullable=False)
    product_name = db.Column(db.String(50), nullable=False)
    product_qty = db.Column(db.Integer, nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    date_updated = db.Column(db.DateTime, default=datetime.utcnow)
    Flag = db.Column(db.String(50),nullable=False)
    def __repr__(self):
    	return 'Movement'+str(self.id)

@app.route('/')
@app.route('/home')
def home():
	message=None
	inventory_details = get_data()
	if not inventory_details:
			message = "Currently Data is unavailable.Add Now!"

	return render_template('index.html',details=inventory_details,message=message)


@app.route('/download_pdf')
def download_pdf():
	
	
	inventory_details = get_data()

	rendered =render_template('download_pdf.html',details=inventory_details)
	css = ['main.css']
	pdf = pdfkit.from_string(rendered,False,configuration=config,css=css)

	response = make_response(pdf)
	response.headers["Content-Type"] = "application/pdf"
	response.headers['Content-Dispostion'] ='inline; filename=output.pdf'
	
	return response

@app.route('/product', methods=['GET','POST'])
def products():
	if request.method=='POST':
		if 'add_product_name' in request.form:
			product_name = request.form['add_product_name']
			if not product_name.strip():
				flash(f"Product name is empty or contains only spaces!", "danger")
				return redirect('/product')
			elif bool(Product.query.filter(func.lower(Product.name) == func.lower(product_name)).first()):
				flash(f"'{product_name}' already exists!", "danger")
				return redirect('/product')
			else:
				new_product=Product(name=product_name)
				db.session.add(new_product)
				db.session.commit()
				flash(f"'{product_name}' is successfully added!", "success")
				return redirect('/product')
		
		if 'delete_product_id' in request.form:
			product_id = request.form['delete_product_id']
			product_name = ProductMovement.query.filter(ProductMovement.product_id==product_id,ProductMovement.Flag =='A').first() 
			if product_name is not None:
				flash(f"'Product used in movement cannot be deleted!", "danger")
				return redirect('/product')
			else:
				delete_product = Product.query.get_or_404(product_id)
				db.session.delete(delete_product)
				db.session.commit()
				flash(f"'{delete_product.name}' is successfully deleted!", "danger")
				return redirect('/product')


		if 'editproduct' in request.form:
			update_product_name = request.form['product_name']
			if bool(Product.query.filter(func.lower(Product.name) == func.lower(update_product_name)).first()):
				flash(f"'{update_product_name}' already exists!", "danger")
				return redirect('/product')
			else:
				update_product_id = request.form['editproduct']
				update = Product.query.get_or_404(update_product_id)
				e_id=ProductMovement.query.filter_by(product_id=update_product_id)
				for  i in e_id:
					edit_movement = ProductMovement.query.get_or_404(i.id)
					edit_movement.product_name=update_product_name
				update.name = update_product_name
				update.date_updated = datetime.utcnow()
				db.session.commit()
				flash(f" Product successfully updated!", "info")
				return redirect('/product')
	else:
		all_product = Product.query.order_by(Product.id).all()
		message = None
		product_details = get_data("product")
		if not product_details:
			message = "Currently Data is unavailable.Add Now!"
		
		return render_template('product.html',product_details=product_details,message=message)

@app.route('/location',methods=['GET','POST'])
def locations():
	if request.method=='POST':
		if 'add_location_name' in request.form:
			location_name = request.form['add_location_name']
			if not location_name.strip():
				flash(f"warehouse is empty or contains only spaces!", "danger")
				return redirect('/location')
			elif bool(Location.query.filter(func.lower(Location.name) == func.lower(location_name)).first()):
				flash(f"'{location_name}' warehouse already exists in the data!", "danger")
				return redirect('/location')
			else:
				new_location=Location(name=location_name)
				db.session.add(new_location)
				db.session.commit()
				flash(f"'{location_name}' warehouse is successfully added!", "success")
				return redirect('/location')

		if 'delete_location_id' in request.form:
			location_id = request.form['delete_location_id']
			old_location_name = Location.query.filter_by(id=location_id).first() 
			f_id=ProductMovement.query.filter(or_(ProductMovement.from_location == old_location_name.name,ProductMovement.to_location == old_location_name.name),ProductMovement.Flag =='A').first()
			if f_id is not None:
				flash(f" Location used in movement cannot be deleted !", "danger")
				return redirect('/location')
			else:
				delete_location = Location.query.get_or_404(location_id)
				db.session.delete(delete_location)
				db.session.commit()
				flash(f"'{delete_location.name}' warehouse successfully deleted", "danger")
				return redirect('/location')

		if 'editlocation' in request.form:
			update_location_name = request.form['location_name']
			if bool(Location.query.filter(func.lower(Location.name) == func.lower(update_location_name)).first()):
				flash(f"'{update_location_name}' warehouse already exists in the data!", "danger")
				return redirect('/location')
			else:
				update_location_id = request.form['editlocation']
				old_location_name = Location.query.filter_by(id=update_location_id).first() 
				update = Location.query.get_or_404(update_location_id)
				f_id=ProductMovement.query.filter_by(from_location = old_location_name.name)
				for  i in f_id:
					edit_movement = ProductMovement.query.get_or_404(i.id)
					edit_movement.from_location=update_location_name
				t_id=ProductMovement.query.filter_by(to_location=old_location_name.name)
				for  i in t_id:
					edit_movement = ProductMovement.query.get_or_404(i.id)
					edit_movement.to_location=update_location_name
				update.name = update_location_name
				update.date_updated = datetime.utcnow()
				db.session.commit()
				flash(f" Warehouse successfully updated to '{update.name}'!", "info")
				return redirect('/location')
	else:
		all_location = Location.query.order_by(Location.id).all()
		location_details = get_data("location")
		message=None
		if not location_details:
			message = "Currently Data is unavailable. Add Now!"
		return render_template('location.html',location_details=location_details,message=message)


@app.route('/movement', methods=['GET','POST'])
def movement():
	if request.method=='POST':
		if 'add_product_qty' in request.form:
			check = None 
			product_name = request.form['product_name']
			from_location = request.form['from_location']
			to_location = request.form['to_location']
			product_qty = request.form['add_product_qty']
			if product_name == 'Select product':
				flash(f"Please select product to add movement!", "danger")
				return redirect('/movement')
			elif int(product_qty) == 0 or int(product_qty) < 0:
				flash(f"Please add quantity !", "danger")
				return redirect('/movement')
			elif from_location == to_location :
				flash(f"From Location & To Location cannot be same!", "danger")
				return redirect('/movement')
			else:
				product_details = Product.query.filter_by(name=product_name).first()
				add_movement=ProductMovement()
				add_movement.product_id=product_details.id
				add_movement.product_name=product_details.name
				
				check_location = ProductMovement.query.filter_by(product_name=product_name).filter_by(to_location=from_location,Flag='A').count()
				if from_location == 'Select Location':
					add_movement.from_location="---"
					add_movement.to_location=to_location
				elif to_location == 'Select Location':
					add_movement.to_location = "---"
					add_movement.from_location=from_location
				elif check_location == 0 and from_location != 'Select Location':
					flash(f"Product not available at '{from_location}' Warehouse !", "danger")
					return redirect('/movement')
				else:
					add_movement.from_location=from_location
					add_movement.to_location=to_location

				sum_qty = get_total(product_name,from_location)
				
				if int(product_qty) > sum_qty and from_location != 'Select Location':
					flash(f" Only {sum_qty} quantity is available at '{from_location}' Warehouse !", "danger")
					return redirect('/movement')
				else:
					add_movement.product_qty=product_qty
				add_movement.Flag = 'A'
				db.session.add(add_movement)
				db.session.commit()
				flash(f" '{add_movement.product_name}' movement is successfully added!", "success")
				return redirect('/movement')

		if 'delete_movement_id' in request.form:
			movement_id = request.form['delete_movement_id']
			product_name = request.form['delete_product_name']
			to_location = request.form['delete_to_location']
			fcheck_qty = get_export_data(product_name,to_location,movement_id,"future")
			fcheck_qty= fcheck_qty.first()
			if fcheck_qty is None :
				delete_movement = ProductMovement.query.get_or_404(movement_id)
				flash(f"{product_name} movement successfully deleted", "danger")
				delete_movement.Flag = 'I'
				db.session.commit()
				return redirect('/movement')

			if fcheck_qty is not None:
				flash(f" Please delete {fcheck_qty.from_location} to {fcheck_qty.to_location} movement before current movement !", "danger")
				return redirect('/movement')
			


		if 'edit_movement' in request.form :
			valid = True
			movement_id = request.form['edit_movement']
			product_name = request.form['product_name']
			from_location = request.form['from_location']
			to_location = request.form['to_location']
			product_qty = request.form['product_qty']
			product_details = Product.query.filter_by(name=product_name).first()
			edit_movement = ProductMovement.query.get_or_404(movement_id)

			if from_location == "---":
				past_sum_qty = get_total(product_name,to_location,movement_id,"past")
			else :
				past_sum_qty = get_total(product_name,from_location,movement_id,"past")

			if to_location == "---" :
				future_sum_qty = get_total(product_name,from_location,movement_id,"future")
			else :
				future_sum_qty = get_total(product_name,to_location,movement_id,"future")
			
			if from_location == to_location : #from location & to location cant be same.
				valid = False
				flash(f"From Location & To Location cannot be same!", "danger")
				return redirect('/movement')
			if int(product_qty) == 0 or int(product_qty) < 0: # qty cant 0
				valid = False
				flash(f"Please add quantity !", "danger")
				return redirect('/movement')
			
			
			if from_location == "---": #min quantity according to future 

				if future_sum_qty != 0:
					if int(product_qty) >= int(future_sum_qty):
						valid = True
					else :
						valid=False
						flash(f"Please add atleast {future_sum_qty} quantity of {product_name} at '{to_location}' Warehouse !", "danger")
						return redirect('/movement')
				
			if (future_sum_qty) == 0:

				if int(product_qty) <= past_sum_qty: # past>qty>future
					valid=True		
				elif int(product_qty) > past_sum_qty and from_location != '---': #past<qty & from location is empty
					valid=False
					if past_sum_qty == 0: #Product not available at past location
						flash(f"Product not available at '{from_location}' Warehouse !", "danger")
						return redirect('/movement')
					elif to_location == "---" : #Quantity available at past location
						valid = False
						flash(f" Only {past_sum_qty} quantity is available at '{from_location}' Warehouse !", "danger")
						return redirect('/movement')
					else :
						valid = False
						flash(f" Please enter quantity less than {past_sum_qty} for '{from_location}' to {to_location} movement !", "danger")
						return redirect('/movement')
				
			elif past_sum_qty < future_sum_qty:
				if int(product_qty) < past_sum_qty and int(product_qty) < future_sum_qty:
					valid=True
				if (int(product_qty) > past_sum_qty or int(product_qty) > future_sum_qty) and from_location != '---':
					flash(f" Please enter quantity less than {past_sum_qty}  for  '{from_location}' to {to_location} movement !", "danger")
					return redirect('/movement')

			elif int(product_qty) <= past_sum_qty and int(product_qty) >= future_sum_qty :
				valid=True

			elif past_sum_qty <= int(product_qty) and from_location == "---" and int(product_qty) >= future_sum_qty :
				valid=True
			else:
				if int(product_qty) > past_sum_qty and int(product_qty) < future_sum_qty:
					valid=False
					flash(f" Please enter quantity {past_sum_qty} or less than {past_sum_qty} for  '{from_location}' to {to_location} movement !", "danger")
					return redirect('/movement')
				elif int(product_qty) < past_sum_qty and int(product_qty) < future_sum_qty:
					valid=False
					flash(f"Please add atleast {future_sum_qty} quantity of {product_name} for '{from_location}' to {to_location} movement !", "danger")
					return redirect('/movement')
				else:
					valid=False
					if past_sum_qty > future_sum_qty:
						flash(f" Please enter quantity {past_sum_qty} or less than {past_sum_qty} for  '{from_location}' to {to_location} movement !", "danger")
					else:
						flash(f" Please enter quantity between {past_sum_qty} to {future_sum_qty}  for  '{from_location}' to {to_location} movement !", "danger")
					return redirect('/movement')
			
			if valid :
				edit_movement.product_id=product_details.id
				edit_movement.product_name=product_details.name
				edit_movement.from_location=from_location
				edit_movement.to_location=to_location
				edit_movement.product_qty=product_qty
				edit_movement.date_updated = datetime.utcnow()
				db.session.commit()
				flash(f"'{edit_movement.product_name}' movement is successfully edited!", "success")
				return redirect('/movement')



	else:
		all_product = Product.query.all()
		all_location = Location.query.all()
		all_movement = ProductMovement.query.filter_by(Flag="A").order_by(ProductMovement.id).all()
		message=None
		if not all_movement:
			message = "Currently Data is unavailable.Add Now!"
		return render_template('movement.html',products=all_product,locations=all_location,movements=all_movement,message=message)
	
	

def get_total(product, location,movement=None,process=None):
	imported = 0
	exported = 0
	
	if movement is None:
		imported_items = get_import_data(product,location)
	else:
		imported_items = get_import_data(product,location,movement,process)
	if imported_items:
		for item in imported_items:
			imported +=item.product_qty
	if movement is None:
		exported_items = get_export_data(product,location)
	else :
		exported_items = get_export_data(product,location,movement,process)
	if exported_items:
			for item in exported_items:
				exported += item.product_qty

	if exported > imported:
		total = exported - imported
	else:
		total = imported - exported
	return total


def get_import_data(product, location,movement=None,process=None):
	if movement is not None:
		if process == 'past':
			imported = ProductMovement.query.filter(ProductMovement.id < movement , ProductMovement.product_name == product ,ProductMovement.to_location == location ,ProductMovement.Flag =='A')
		if process == 'future':
			imported = ProductMovement.query.filter(ProductMovement.id > movement , ProductMovement.product_name == product ,ProductMovement.to_location == location ,ProductMovement.Flag =='A')
	else:
		imported = ProductMovement.query.filter_by(product_name=product).filter_by(to_location=location).filter_by(Flag='A').all()

	return imported

def get_export_data(product, location,movement=None,process=None):
	if movement is not None:
		if process == 'past':
			exported = ProductMovement.query.filter(ProductMovement.id < movement , ProductMovement.product_name == product ,ProductMovement.from_location == location ,ProductMovement.Flag =='A')
			return exported
		if process == 'future':
			exported = ProductMovement.query.filter(ProductMovement.id > movement , ProductMovement.product_name == product ,ProductMovement.from_location == location ,ProductMovement.Flag =='A')
			return exported
	else:
		exported = ProductMovement.query.filter_by(product_name=product).filter_by(from_location=location).filter_by(Flag='A').all()
		return exported
	

def get_data(process=None):
	all_data=[]
	products = Product.query.all()
	locations = Location.query.all()
	total_qty = 0
	
	if process=="product":

		for product in products:
			data = {}
			prod_name = product.name
			prod_id = product.id
			data['id'] = prod_id
			data['name'] = prod_name
			for location in locations:
				loc_name = location.name
				total = get_total(prod_name,loc_name)
				if total == 0:
					continue
				else:
					 total_qty += total
			if total_qty == 0 :
				data['available_quantity'] = '---'
			else :
				data['available_quantity'] = total_qty
			total_qty=0
			all_data.append(data)
		return all_data
	
	elif process == "location":
		for location in locations:
			data = {}
			prod_data = []
			loc_name = location.name
			loc_id = location.id
			data['id'] = loc_id
			data['name'] = loc_name
			for product in products:
				
				prod_name = product.name
				total = get_total(prod_name,loc_name)
				
				if total == 0:
					continue
				else:
					prod_data.append(prod_name)
					
			res = str(prod_data)[1:-1]
			res = res.replace("'", "")
			data['prod_list']=res
			all_data.append(data)
		return all_data
	else:

		for product in products:
			for location in locations:
				data = {}
				prod_name = product.name
				loc_name = location.name
				total = get_total(prod_name,loc_name)
				
				if total == 0:
					continue
				else:
					data['product'] = prod_name
					data['location'] = loc_name
					data['available_quantity'] = total
				all_data.append(data)
		return all_data




if __name__=='__main__':
	app.run(debug=True)
