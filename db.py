from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

association_table = db.Table(
    "association",
    db.Model.metadata,
    db.Column("machine_id", db.Integer, db.ForeignKey("machine.id")),
    db.Column("item_id", db.Integer, db.ForeignKey("item.id")),
)

class Machine(db.Model):
    """Machine Model"""
    __tablename__ = "machine"
    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    coordinate = db.Column(db.String, nullable = False)
    status = db.Column(db.Boolean, nullable = False)
    brbs = db.Column(db.Boolean, nullable = False)
    itemtype = db.Column(db.String, nullable = False)
    items = db.relationship("Item", secondary = association_table, back_populates = "machines")
    location_id = db.Column(db.Integer, db.ForeignKey("location.id"), nullable = False)

    def __init__(self, **kwargs):
        """initialize a Course"""
        self.coordinate = kwargs.get("coordinate")
        self.status = kwargs.get("status")
        self.brbs = kwargs.get("brbs")
        self.itemtype = kwargs.get("itemtype")
        self.location_id = kwargs.get("location_id")

    def serialize(self):  
        """serialize a Course"""  
        return {        
            "id": self.id,
            "coordinate": self.coordinate,
            "status": self.status,
            "brbs": self.brbs,
            "itemtype": self.itemtype,
            "items": [i.simple_serialize() for i in self.items],
            "location": Location.query.filter_by(id=self.location_id).first().simple_serialize()
        }

    def simple_serialize(self):  
        """serialize a Course"""  
        return {        
            "id": self.id,
            "coordinate": self.coordinate,
            "status": self.status,
            "brbs": self.brbs,
            "itemtype": self.itemtype,
        }


class Item(db.Model):
    """Item Model"""
    __tablename__ = "item"
    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    name = db.Column(db.String, nullable = False)
    machines = db.relationship("Machine", secondary = association_table, back_populates = "items")
    
    def __init__(self, **kwargs):
        """initialize a Item"""
        self.name = kwargs.get("name")

    def serialize(self): 
        """serialize a Item"""    
        return {
            "id": self.id,
            "name": self.name,
            "machines": [m.simple_serialize() for m in self.machines]
        }
            
    def simple_serialize(self):  
        """serialize a Item without machine field"""  
        return {        
            "id": self.id,
            "name": self.name
        }

class Location(db.Model):
    """Location Model"""
    __tablename__ = "location"
    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    location = db.Column(db.String, nullable = False)
    machines = db.relationship("Machine", cascade = "delete")

    def __init__(self, **kwargs):
        """Initialize a location"""
        self.location = kwargs.get("location")

    def serialize(self):
        """Serialize a location"""
        return {
            "id": self.id,
            "location": self.location,
            "machines": [m.simple_serialize() for m in self.machines]
        }
    
    def simple_serialize(self):
        """Serialize a location without the machines field"""
        return {
            "id": self.id,
            "location": self.location
        }
