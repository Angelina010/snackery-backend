from db import db, Machine, Item
from flask import Flask, request
import json



app = Flask(__name__)
db_filename = "cms.db"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///%s" % db_filename
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True

db.init_app(app)
with app.app_context():
    db.create_all()


def failure_response(message, code=404):
    return json.dumps({'error': message}), code


#machines
@app.route("/api/machines/", methods = ["POST"])
def create_machine():
    """create a machine based on info given by user"""
    body = json.loads(request.data)
    new_machine = Machine(coordinate = body.get("coordinate"), status = body.get("status"), \
    brbs = body.get("brbs"), itemtype  = body.get("itemtype"))
    db.session.add(new_machine)
    db.session.commit()
    return json.dumps(new_machine.serialize()), 201

@app.route("/api/machines/<int:id>/", methods = ["DELETE"])
def delete_machine(id):
    """delete machine by id"""
    machine = Machine.query.filter_by(id = id).first()
    if machine is None:
        return failure_response("Machine not found.")
    db.session.delete(machine)
    db.session.commit()
    return json.dumps(machine.serialize()), 200

@app.route("/api/machines/<int:id>/add/", methods = ["POST"])
def update_status(id):
    """change status of machine by id"""
    machine = Machine.query.filter_by(id = id).first()
    if machine is None:
        return failure_response("Machine not found.")
    body = json.loads(request.data)
    new_status = body.get("status")

    machine.status = new_status
    db.session.commit()
    return json.dumps(machine.serialize()), 200


#items
@app.route("/api/items/", methods = ["POST"])
def create_item():
    """create new item, can be sold at none of the machines or multiple"""
    body = json.loads(request.data)
    new_item = Item(name = body.get("name"))
    db.session.add(new_item)
    db.session.commit()
    return json.dumps(new_item.serialize()), 201

@app.route("/api/courses/<int:machine_id>/", methods = ["POST"])
def update_machine(machine_id):
    """add or delete item from one machine by machine id"""
    machine = Machine.query.filter_by(id = id).first()
    if machine is None:
        return failure_response("Machine not found.")
    body = json.loads(request.data)
    item_id = body.get("item_id")
    action = body.get("action")

    item = Item.query.filter_by(id = item_id).first()
    if item is None:
        return failure_response("Item not found.")
    
    if action == "add":
        machine.items.append(item)
    if action == "delete":
        old_items = machine.items
        temp = None
        for i in range(len(old_items)):
            if old_items[i] == item:
                temp = machine.items.pop(i)
        if temp is None: 
            return failure_response("Item is not available at this machine.")
    
    db.session.commit()
    return json.dumps(machine.serialize()), 200
