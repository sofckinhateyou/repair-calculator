# models.py
class Customer:
    def __init__(self, id=None, name="", phone="", email=""):
        self.id = id
        self.name = name
        self.phone = phone
        self.email = email

    def __str__(self):
        return f"{self.name} ({self.phone})"


class Executor:
    def __init__(self, id=None, name="", phone="", company_name="", rating=0.0):
        self.id = id
        self.name = name
        self.phone = phone
        self.company_name = company_name
        self.rating = rating

    def __str__(self):
        return f"{self.name} ({self.company_name}, {self.rating}★)"


class Room:
    def __init__(self, id=None, room_type="", area_m2=0.0, floor=1, building_id=1, customer_id=1):
        self.id = id
        self.room_type = room_type
        self.area_m2 = area_m2
        self.floor = floor
        self.building_id = building_id
        self.customer_id = customer_id

    def __str__(self):
        return f"{self.room_type} ({self.area_m2} м², этаж {self.floor})"


class Material:
    def __init__(self, id=None, name="", unit="", price_per_unit=0.0, category=""):
        self.id = id
        self.name = name
        self.unit = unit
        self.price_per_unit = price_per_unit
        self.category = category

    def __str__(self):
        return f"{self.name} ({self.unit}, {self.price_per_unit} руб)"


class WorkType:
    def __init__(self, id=None, name="", unit="", price_per_unit=0.0, category=""):
        self.id = id
        self.name = name
        self.unit = unit
        self.price_per_unit = price_per_unit
        self.category = category

    def __str__(self):
        return f"{self.name} ({self.unit}, {self.price_per_unit} руб)"


class JobItem:
    def __init__(self, id=None, room_id=1, work_type_id=1, material_id=None, quantity=0.0, total_price=0.0):
        self.id = id
        self.room_id = room_id
        self.work_type_id = work_type_id
        self.material_id = material_id
        self.quantity = quantity
        self.total_price = total_price

    def __str__(self):
        return f"{self.quantity} {self.get_unit()} → {self.total_price} руб"