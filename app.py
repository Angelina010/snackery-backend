from db import db, Machine, Item, Location
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

@app.route("/")
def base():
    """base endpoint"""
    return "Welcome to Snackery!"

#machines
@app.route("/api/machines/")
def get_machines():
    """get all machines"""
    machines = [m.serialize() for m in Machine.query.all()]
    return json.dumps({"machines": machines}), 200

@app.route("/api/machines/<int:id>/")
def get_machine(id):
    """get machine by id"""
    machine = Machine.query.filter_by(id = id).first()
    if machine is None:
        return failure_response("Machine not found.")
    return json.dumps(machine.serialize()), 200

@app.route("/api/machines/working/")
def get_working_machines():
    """get all currently working machines"""
    machines = [m.serialize() for m in Machine.query.all() if m.status]
    return json.dumps({"machines": machines}), 200

@app.route("/api/machines/brbs/")
def get_brb_machines():
    """get all machines that accept BRBs"""
    machines = [m.serialize() for m in Machine.query.all() if m.brbs]
    return json.dumps({"machines": machines}), 200

@app.route("/api/machines/<int:location_id>/", methods = ["POST"])
def create_machine(location_id):
    """create a machine at the location with the given id based on info given by user"""
    location = Location.query.filter_by(id = location_id).first()
    if location is None:
        return failure_response("Location not found.")
    body = json.loads(request.data)
    new_coordinate = body.get("coordinate")
    if not new_coordinate:
        return failure_response("Invalid request: Please provide a coordinate.", 400)
    if not isinstance(new_coordinate, str):
        return failure_response("Invalid request: Coordinate must be a string.", 400)
    new_status = body.get("status")
    if new_status is None:
        return failure_response("Invalid request: Please provide a status.", 400)
    if not isinstance(new_status, bool):
        return failure_response("Invalid request: Status must be a boolean.", 400)
    new_brbs = body.get("brbs")
    if new_brbs is None:
        return failure_response("Invalid request: Please provide a BRBs input.", 400)
    if not isinstance(new_brbs, bool):
        return failure_response("Invalid request: BRBs must be a boolean.", 400)
    new_itemtype = body.get("itemtype")
    if not new_itemtype:
        return failure_response("Invalid request: Please provide an item type.", 400)
    if not isinstance(new_itemtype, str):
        return failure_response("Invalid request: Item type must be a string.", 400)
    new_machine = Machine(coordinate = new_coordinate, status = new_status, \
    brbs = new_brbs, itemtype  = new_itemtype, location_id = location_id)
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
    if new_status is None:
        return failure_response("Invalid request: Please provide a status.", 400)
    if not isinstance(new_status, bool):
        return failure_response("Invalid request: Status must be a boolean.", 400)

    machine.status = new_status
    db.session.commit()
    return json.dumps(machine.serialize()), 200

#locations
@app.route("/api/locations/", methods = ["POST"])
def create_location():
    """create a new location"""
    body = json.loads(request.data)
    loc = body.get("location")
    if not loc:
        return failure_response("Invalid request: Please provide a location.", 400)
    if not isinstance(loc, str):
        return failure_response("Invalid request: Location must be a string.", 400)
    new_location = Location(location = loc)
    db.session.add(new_location)
    db.session.commit()
    return json.dumps(new_location.serialize()), 201

@app.route("/api/locations/<int:id>/")
def get_machines_by_location(id):
    """get all machines at the location with the given id"""
    location = Location.query.filter_by(id = id).first()
    if location is None:
        return failure_response("Location not found.")
    machines = [m.serialize() for m in location.machines]
    return json.dumps({"machines": machines}), 200

#items
@app.route("/api/items/<int:id>/")
def find_item(id):
    """get all machines that have the item with the given id"""
    item = Item.query.filter_by(id = id).first()
    if item is None:
        return failure_response("Item not found.")
    
    machines = [m.serialize() for m in Machine.query.all() if item in m.items]
    return json.dumps({"machines": machines}), 200

@app.route("/api/items/", methods = ["POST"])
def create_item():
    """create new item, can be sold at none of the machines or multiple"""
    body = json.loads(request.data)
    new_name = body.get("name")
    if not new_name:
        return failure_response("Invalid request: Please provide a name.", 400)
    if not isinstance(new_name, str):
        return failure_response("Invalid request: Name must be a string.", 400)
    new_item = Item(name = new_name)
    db.session.add(new_item)
    db.session.commit()
    return json.dumps(new_item.serialize()), 201

@app.route("/api/items/<int:id>/", methods = ["DELETE"])
def delete_item(id):
    """delete item by id"""
    item = Item.query.filter_by(id = id).first()
    if item is None:
        return failure_response("Item not found.")
    db.session.delete(item)
    db.session.commit()
    return json.dumps(item.serialize()), 200

@app.route("/api/items/<int:machine_id>/", methods = ["POST"])
def update_machine(machine_id):
    """add or delete item from one machine by machine id"""
    machine = Machine.query.filter_by(id = machine_id).first()
    if machine is None:
        return failure_response("Machine not found.")
    body = json.loads(request.data)
    item_id = body.get("item_id")
    if item_id is None:
        return failure_response("Invalid request: Please provide an item id.", 400)
    if not isinstance(item_id, int):
        return failure_response("Invalid request: Item id must be an integer.", 400)
    action = body.get("action")
    if not action:
        return failure_response("Invalid request: Please provide an action.", 400)
    if not isinstance(action, str):
        return failure_response("Invalid request: Action must be a string.", 400)

    item = Item.query.filter_by(id = item_id).first()
    if item is None:
        return failure_response("Item not found.")
    
    if action == "add":
        machine.items.append(item)
    elif action == "delete":
        old_items = machine.items
        temp = None
        for i in range(len(old_items)):
            if old_items[i] == item:
                temp = machine.items.pop(i)
        if temp is None: 
            return failure_response("Item is not available at this machine.")
    else:
        return failure_response("Invalid request: This action is unsupported. Please try either 'add' or 'delete'.", 400)
    
    db.session.commit()
    return json.dumps(machine.serialize()), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)