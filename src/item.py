from abc import ABC
import operator
from datetime import datetime

#TODO: optional catagories. Would like to add a dict for nutritional value if provided
class Item():
    """Class for an item sold by the grocery store."""
    def __init__(self, name, brand, price, sale_price=None, on_sale=False, tax_category=""):
        self.name = name
        self.brand = brand
        self.price = price
        self.sale_price = sale_price
        self.on_sale = on_sale
        self.tax_category = tax_category
        self.timestamp = datetime.now() 


    name = property(operator.attrgetter("_name"))

    @name.setter
    def name(self, n):
        if not n: raise ValueError("Item name required")
        self._name = str(n)

    brand = property(operator.attrgetter("_brand"))

    @brand.setter
    def brand(self, b):
        self._brand = str(b)

    price = property(operator.attrgetter("_price"))

    @price.setter
    def price(self, p):
        try: 
            p = float(p)
        except: 
            raise ValueError("Item must have a valid price (i.e. 1.50)")
        if not p > 0.0: raise ValueError("Item must have a price greater than 0.0")
        #TODO: make this more robust with regards to FP arithmetic limitations
        # (i.e. 2.675 rounds to 2.67)
        self._price = format(p, ".2f") 

    sale_price = property(operator.attrgetter("_sale_price"))

    @sale_price.setter
    def sale_price(self, p):
        if p == "" or p == "?" or p == None:
            self._sale_price = None
        else:
            try: 
                p = float(p)
            except: 
                raise ValueError("Item must have a valid price (i.e. 1.50)")
            if not p > 0.0: raise ValueError("Item must have a price greater than 0.0")
            #TODO: make this more robust with regards to FP arithmetic limitations
            # (i.e. 2.675 rounds to 2.67)
            self._sale_price = format(p, ".2f") 


    on_sale = property(operator.attrgetter("_on_sale"))

    @on_sale.setter
    def on_sale(self, s):
        if not isinstance(s, bool):
            raise ValueError("Item must have type {} for on_sale variable. Got {} instead".format(bool, type(s)))
        self._on_sale = s

    tax_category = property(operator.attrgetter("_tax_category"))

    @tax_category.setter
    def tax_category(self, tc):
        if tc == "": 
            self._tax_category = None
        else:
            self._tax_category = str(tc)

i = Item("shit", "asfd", 1, .55, False, "")
print("Name: {}\nBrand: {}\nPrice: {}\nSale Price: {}\nOn Sale: {}\nTax Category: {}\n".format(
    i.name, i.brand, i.price, i.sale_price, i.on_sale, i.tax_category))
