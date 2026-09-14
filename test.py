import openmc
import numpy as np


water = openmc.Material(name="water")
water.add_nuclide("H1", 2.0)
water.add_nuclide("O16", 1.0)
water.set_density("g/cm3", 1.0)

lib = openmc.data.DataLibrary.from_xml()
path = lib.get_by_material("H1")

print("Fant data fir H1 her:", path)