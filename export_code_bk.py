from flask import Flask,render_template,url_for,redirect,request,flash,make_response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
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

@app.route('/')
@app.route('/home')
def home():
	inventory_details = get_data()

	return render_template('index.html',title='Inventory Management',details=inventory_details)

	


@app.route('/download_pdf')
def download_pdf():
	
	
	inventory_details = get_data()

	rendered =render_template('download_pdf.html',details=inventory_details)
	css = ['main.css']
	pdf = pdfkit.from_string(rendered,False,configuration=config,css=css)

	response = make_response(pdf)
	response.headers["Content-Type"] = "application/pdf"
	response.headers['Content-Dispostion'] ='inline; filename=output.pdf'
	#response.headers['Content-Dispostion'] ='attachment; filename=output.pdf'
	
	return response

@app.route('/product', methods=['GET','POST'])
def products():
	if request.method=='POST':
		if 'add_product_name' in request.form:
			product_name = request.form['add_product_name']
			if not product_name.strip():
				flash(f"Product name is empty or contains only spaces!", "danger")
				return redirect('/product')
			elif bool(Product.query.filter_by(name=product_name).first()):
				flash(f"'{product_name}' warehouse already exists in the data!", "danger")
				return redirect('/product')
			else:
				new_product=Product(name=product_name)
				db.session.add(new_product)
				db.session.commit()
				flash(f"'{product_name}' warehouse is successfully added!", "success")
				return redirect('/product')
		
		if 'delete_product_id' in request.form:
			product_id = request.form['delete_product_id']
			delete_product = Product.query.get_or_404(product_id)
			db.session.delete(delete_product)
			db.session.commit()
			flash(f"'{delete_product.name}' is successfully deleted!", "danger")
			return redirect('/product')


		if 'editproduct' in request.form:
			update_product_name = request.form['product_name']
			if bool(Product.query.filter_by(name=update_product_name).first()):
				flash(f"'{update_product_name}' warehouse already exists in the data!", "danger")
				return redirect('/product')
			else:
				update_product_id = request.form['editproduct']
				update = Product.query.get_or_404(update_product_id)
				update.name = update_product_name
				update.date_updated = datetime.utcnow()
				db.session.commit()
				flash(f" Warehouse successfully updated to '{update.name}'!", "info")
				return redirect('/product')
	else:
		all_product = Product.query.order_by(Product.id).all()
		return render_template('product.html',title='Post',products=all_product)

@app.route('/location',methods=['GET','POST'])
def locations():
	if request.method=='POST':
		if 'add_location_name' in request.form:
			location_name = request.form['add_location_name']
			if not location_name.strip():
				flash(f"warehouse is empty or contains only spaces!", "danger")
				return redirect('/location')
			elif bool(Location.query.filter_by(name=location_name).first()):
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
			delete_location = Location.query.get_or_404(location_id)
			db.session.delete(delete_location)
			db.session.commit()
			flash(f"'{delete_location.name}' warehouse successfully deleted", "danger")
			return redirect('/location')

		if 'editlocation' in request.form:
			update_location_name = request.form['location_name']
			if bool(Location.query.filter_by(name=update_location_name).first()):
				flash(f"'{update_location_name}' warehouse already exists in the data!", "danger")
				return redirect('/location')
			else:
				update_location_id = request.form['editlocation']
				update = Location.query.get_or_404(update_location_id)
				update.name = update_location_name
				update.date_updated = datetime.utcnow()
				db.session.commit()
				flash(f" Warehouse successfully updated to '{update.name}'!", "info")
				return redirect('/location')
	else:
		all_location = Location.query.order_by(Location.id).all()
		return render_template('location.html',title='Location',locations=all_location)


@app.route('/movement', methods=['GET','POST'])
def movement():
	if request.method=='POST':
		if 'add_product_qty' in request.form:
			i_sum_qty = []
			e_sum_qty = []
			check = None 
			product_name = request.form['product_name']
			from_location = request.form['from_location']
			to_location = request.form['to_location']
			product_qty = request.form['add_product_qty']
			if product_name == 'Select product':
				flash(f"Please select product to add movement!", "danger")
				return redirect('/movement')
			elif bool(ProductMovement.query.filter_by(product_name=product_name,from_location=from_location,to_location=to_location,product_qty=product_qty,Flag='A').first()):
				flash(f" movement already exists in the data!", "danger")
				return redirect('/movement')
			# elif to_location == 'Select Location':
			# 	flash(f"Please select destination location !", "danger")
			# 	return redirect('/movement')
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
				
				check_location = ProductMovement.query.filter_by(product_name=product_name).filter_by(to_location=from_location).count()
				if from_location == 'Select Location':
					check="from_location"
					add_movement.from_location="---"
					add_movement.to_location=to_location
				elif to_location == 'Select Location':
					check="to_location"
					add_movement.to_location = "---"
					add_movement.from_location=from_location
				elif check_location == 0 and from_location != 'Select Location':
					flash(f"Product not available at '{from_location}' Warehouse !", "danger")
					return redirect('/movement')
				else:
					add_movement.from_location=from_location
					add_movement.to_location=to_location

				
				if check=="to_location":
					add_movement.from_location=from_location
				if check=="from_location":
					add_movement.to_location=to_location
				sum_qty = get_total(product_name,from_location)
				#e_sum_qty = get_total(product_name,from_location)

				# import_qty = ProductMovement.query.filter(ProductMovement.product_name == product_name ,ProductMovement.to_location == from_location)
				# export_qty = ProductMovement.query.filter(ProductMovement.product_name == product_name ,ProductMovement.from_location == from_location)
				
				# for e_qty in export_qty :
				# 	j = e_qty.product_qty
				# 	e_sum_qty.insert(0,j)
				# e_sum_qty = sum(e_sum_qty)

				# for i_qty in import_qty :
				# 	i = i_qty.product_qty
				# 	i_sum_qty.insert(0,i)
				# i_sum_qty = sum(i_sum_qty)

				# if from_location == 'Select Location':
				# 	sum_qty=e_sum_qty
				# if e_sum_qty == 0 :
				# 	sum_qty=i_sum_qty
				# if e_sum_qty != 0 and from_location != 'Select Location':
				# 	sum_qty = i_sum_qty - e_sum_qty


				
				if int(product_qty) <= sum_qty:
					add_movement.product_qty=product_qty
				if int(product_qty) > sum_qty and from_location != 'Select Location':
					flash(f" Only {sum_qty} quantity is available at '{from_location}' Warehouse !", "danger")
					return redirect('/movement')
				add_movement.product_qty=product_qty
				add_movement.Flag = 'A'
				#product_id=product_id,product_name=product_name,from_location=from_location,to_location=to_location,product_qty=product_qty
				db.session.add(add_movement)
				db.session.commit()
				flash(f" '{add_movement.product_name}' movement is successfully added!", "success")
				return redirect('/movement')

		if 'delete_movement_id' in request.form:
			movement_id = request.form['delete_movement_id']
			product_name = request.form['delete_product_name']
			to_location = request.form['delete_to_location']
			fcheck_qty = get_exported(product_name,to_location,movement_id,"future")
			fcheck_qty= fcheck_qty.first()
			if fcheck_qty is None :
				delete_movement = ProductMovement.query.get_or_404(movement_id)
				flash(f"{product_name} movement successfully deleted", "danger")
				delete_movement.Flag = 'I'
				#db.session.delete(delete_movement)
				db.session.commit()
				return redirect('/movement')

			if fcheck_qty is not None:
				flash(f" Please delete {fcheck_qty.from_location} to {fcheck_qty.to_location} movement before current movement !", "danger")
				return redirect('/movement')
			


		if 'edit_movement' in request.form :
			pimp_sum_qty = []
			pexp_sum_qty = []
			f_range = None
			valid = True
			fimp_sum_qty = []
			fexp_sum_qty = []
			fimport= None
			movement_id = request.form['edit_movement']
			product_name = request.form['product_name']
			from_location = request.form['from_location']
			to_location = request.form['to_location']
			product_qty = request.form['product_qty']
			product_details = Product.query.filter_by(name=product_name).first()

			if product_details is None:					#Product availibilty check
				flash(f"Product is Not Available/Deleted", "danger")
				return redirect('/movement')

			#pimport_qty = ProductMovement.query.filter(ProductMovement.id < movement_id , ProductMovement.product_name == product_name ,ProductMovement.to_location == from_location)
			#pexport_qty = ProductMovement.query.filter(ProductMovement.id < movement_id , ProductMovement.product_name == product_name ,ProductMovement.from_location == from_location)
			
			if from_location == "---":
				past_sum_qty = get_total(product_name,to_location,movement_id,"past")
			else :
				past_sum_qty = get_total(product_name,from_location,movement_id,"past")

			if to_location == "---" :
				future_sum_qty = get_total(product_name,from_location,movement_id,"future")
			else :
				fimport = ProductMovement.query.filter(ProductMovement.id > movement_id , ProductMovement.product_name == product_name ,ProductMovement.to_location == to_location).first() #take only future from location
				if fimport:
					fimport = fimport.id
					future_sum_qty = get_total(product_name,to_location,movement_id,"future",fimport)
				else:
					future_sum_qty = get_total(product_name,to_location,movement_id,"future")
			#fexport_qty = ProductMovement.query.filter(ProductMovement.id > movement_id , ProductMovement.product_name == product_name ,ProductMovement.from_location == to_location)
			#fimport_qty = ProductMovement.query.filter(ProductMovement.id > movement_id , ProductMovement.product_name == product_name ,ProductMovement.to_location == to_location)
			#fcheck_qty = ProductMovement.query.filter(ProductMovement.id > movement_id , ProductMovement.product_name == product_name ,ProductMovement.from_location == to_location).first()
			edit_movement = ProductMovement.query.get_or_404(movement_id)
			
			# for e_qty in pexport_qty :
			# 	j = e_qty.product_qty
			# 	pexp_sum_qty.insert(0,j)
			# pexp_sum_qty = sum(pexp_sum_qty)

			# for i_qty in pimport_qty :
			# 	i = i_qty.product_qty
			# 	pimp_sum_qty.insert(0,i)
			# pimp_sum_qty = sum(pimp_sum_qty)

			# if pexp_sum_qty > pimp_sum_qty :
			# 	past_sum_qty = pexp_sum_qty - pimp_sum_qty
			# else :
			# 	past_sum_qty = pimp_sum_qty - pexp_sum_qty

			# for fe_qty in fexport_qty :
			# 	a = fe_qty.product_qty
			# 	fexp_sum_qty.insert(0,a)
			# fexp_sum_qty = sum(fexp_sum_qty)

			# for fi_qty in fimport_qty :
			# 	b = fi_qty.product_qty
			# 	fimp_sum_qty.insert(0,b)
			# fimp_sum_qty = sum(fimp_sum_qty)

			# if fexp_sum_qty > fimp_sum_qty :
			# 	future_sum_qty = fexp_sum_qty - fimp_sum_qty
			# else :
			# 	future_sum_qty = fimp_sum_qty - fexp_sum_qty



			if from_location == to_location :
				valid = False
				flash(f"From Location & To Location cannot be same!", "danger")
				return redirect('/movement')
			# if bool(ProductMovement.query.filter_by(product_name=product_name,from_location=from_location,to_location=to_location,product_qty=product_qty).first()):
			# 	valid = False
			# 	flash(f" movement already exists in the data!", "danger")
			# 	return redirect('/movement')
			if int(product_qty) == 0 or int(product_qty) < 0:
				valid = False
				flash(f"Please add quantity !", "danger")
				return redirect('/movement')
			
				
			
			
			#check_location = ProductMovement.query.filter(ProductMovement.id < movement_id , ProductMovement.product_name == product_name ,ProductMovement.to_location == from_location).count() #check if product is available at senders location
			if from_location == "---":

				if future_sum_qty != 0:
					f_range = future_sum_qty

					if int(product_qty) >= int(f_range) :
						valid = True
			
					else :
						valid=False
						flash(f"Please add atleast {future_sum_qty} quantity of {product_name} at '{to_location}' Warehouse !", "danger")
						return redirect('/movement')
				
				# if check_location > 0:
				# 	valid = True
				# if check_location == 0:
				# 	valid = False
				# 	flash(f"Check Product not available at '{from_location}' Warehouse !", "danger")
				# 	return redirect('/movement')
					

				
				
				# pimport_qty = ProductMovement.query.filter(ProductMovement.id < movement_id , ProductMovement.product_name == product_name ,ProductMovement.to_location == from_location)
				# pexport_qty = ProductMovement.query.filter(ProductMovement.id < movement_id , ProductMovement.product_name == product_name ,ProductMovement.from_location == from_location)
				
				# fcheck_qty = ProductMovement.query.filter(ProductMovement.id > movement_id , ProductMovement.product_name == product_name ,ProductMovement.from_location == to_location).first()
				

			

			

			if int(product_qty) <= past_sum_qty and (future_sum_qty) == 0 :
				valid=True
				edit_movement.product_qty=product_qty

					
			elif int(product_qty) > past_sum_qty and (future_sum_qty) == 0 :
				valid=False
				if past_sum_qty == 0:
					flash(f"Product not available at '{from_location}' Warehouse !", "danger")
					return redirect('/movement')
				elif to_location == "---" :
					valid = False
					flash(f" Only {past_sum_qty} quantity is available at '{from_location}' Warehouse !", "danger")
					return redirect('/movement')
				else :
					valid = False
					flash(f" Please enter quantity less than {past_sum_qty} for '{from_location}' to {to_location} movement !", "danger")
					return redirect('/movement')
				
			elif int(product_qty) <= past_sum_qty and int(product_qty) >= future_sum_qty :
				valid=True
				edit_movement.product_qty=product_qty

			elif past_sum_qty <= int(product_qty) and from_location == "---" and int(product_qty) >= future_sum_qty :
				valid=True
				edit_movement.product_qty=product_qty
			else:
				if int(product_qty) > past_sum_qty and int(product_qty) < future_sum_qty:
					valid=False
					flash(f" Please enter quantity {past_sum_qty} or less than {past_sum_qty} for  '{from_location}' to {to_location} movement !", "danger")
					return redirect('/movement')
				elif int(product_qty) < past_sum_qty and int(product_qty) < future_sum_qty:
					
					valid=False
					flash(f" Please enter quantity between {past_sum_qty} to {future_sum_qty}  for  '{from_location}' to {to_location} movement !", "danger")
					return redirect('/movement')
				else:
					valid=False
					flash(f" Please enter quantity between {past_sum_qty} to {future_sum_qty}  for  '{from_location}' to {to_location} movement !", "danger")
					return redirect('/movement')
					

			
			#product_id=product_id,product_name=product_name,from_location=from_location,to_location=to_location,product_qty=product_qty
			if valid :
				edit_movement.product_id=product_details.id
				edit_movement.product_name=product_details.name
				edit_movement.from_location=from_location
				edit_movement.to_location=to_location
				edit_movement.product_qty=product_qty
				edit_movement.date_updated = datetime.utcnow()
				db.session.commit()
				flash(f"'{past_sum_qty} {edit_movement.product_name}'  {future_sum_qty}F movement is successfully edited!", "success")
				return redirect('/movement')



	else:
		all_product = Product.query.order_by(Product.id).all()
		all_location = Location.query.order_by(Location.id).all()
		all_movement = ProductMovement.query.filter_by(Flag="A").order_by(ProductMovement.id).all()
		return render_template('movement.html',title='ProductMovement',products=all_product,locations=all_location,movements=all_movement)
		
	
# @app.route('/delete/<string:name>')
# def delete(name):
# 	var='Mumbaiii4'
# 	if name == var[:6]:
# 		delete_item = Location.query.filter_by(name=name).first()
# 		db.session.delete(delete_item)
# 		db.session.commit()
# 		flash('You were successfully added')
# 		return redirect('/location')
# 	else:
# 		return redirect('/location')



def get_total(product, location,movement=None,process=None,future_import=None):
	imported = 0
	exported = 0
	flash(f" Please {imported}i {process} {movement} {future_import} {exported}e !", "danger")
	if future_import is not None :
		imported_items =0
	else :
		if movement is None:
			imported_items = get_imported(product,location)
		else:
			imported_items = get_imported(product,location,movement,process)
		if imported_items:
			for item in imported_items:
				imported +=item.product_qty
	if movement is None:
		exported_items = get_exported(product,location)
	else :
		exported_items = get_exported(product,location,movement,process)

	if future_import is not None :
		if exported_items:
			for item in exported_items:
				if item.id < future_import:
					exported += item.product_qty
	else:
		if exported_items:
			for item in exported_items:
				exported += item.product_qty

	flash(f" Please {imported}i {process} {movement} {exported}e !", "danger")
	if exported > imported:
		total = exported - imported
	else:
		total = imported - exported
	flash(f" Please {total} !", "danger")
	return total


def get_imported(product, location,movement=None,process=None):
	if movement is not None:
		if process == 'past':
			imported = ProductMovement.query.filter(ProductMovement.id < movement , ProductMovement.product_name == product ,ProductMovement.to_location == location ,ProductMovement.Flag =='A')
		if process == 'future':
			#flash(f" Inside future E!", "danger")
			imported = ProductMovement.query.filter(ProductMovement.id > movement , ProductMovement.product_name == product ,ProductMovement.to_location == location ,ProductMovement.Flag =='A')
	else:
		imported = ProductMovement.query.filter_by(product_name=product).filter_by(to_location=location).filter_by(Flag='A').all()

	return imported

def get_exported(product, location,movement=None,process=None):
	if movement is not None:
		if process == 'past':
			#flash(f" Inside past E!", "danger")
			exported = ProductMovement.query.filter(ProductMovement.id < movement , ProductMovement.product_name == product ,ProductMovement.from_location == location ,ProductMovement.Flag =='A')
			return exported
		if process == 'future':
			#flash(f" Inside future E!", "danger")
			exported = ProductMovement.query.filter(ProductMovement.id > movement , ProductMovement.product_name == product ,ProductMovement.from_location == location ,ProductMovement.Flag =='A')
			return exported
	else:
		flash(f" Inside else E!", "danger")
		exported = ProductMovement.query.filter_by(product_name=product).filter_by(from_location=location).filter_by(Flag='A').all()
		return exported
	





def get_data():
	all_data=[]
	products = Product.query.all()
	locations = Location.query.all()
	for product in products:
		for location in locations:
			data = {}
			prod_name = product.name
			loc_name = location.name
			total = get_total(prod_name,loc_name)
			data['product'] = prod_name
			data['location'] = loc_name
			if total == 0:
				continue
			else:
				data['available_quantity'] = total
			all_data.append(data)

	return all_data




if __name__=='__main__':
	app.run(debug=True)