import numpy as np
import matplotlib.pyplot as plt
import openmc


#Oppretter elementene våre
#-----------------------------------------------------------
urox = openmc.Material(name = "Uranium dioxide")
urox.add_nuclide("U235", 0.02)
urox.add_nuclide("U238", 0.98)
urox.add_element("O", 2.0)
urox.set_density("g/cm3", 10.97)
urox.add_s_alpha_beta("c_O_in_UO2")

unat = openmc.Material(name = "Uran")
unat.add_element("U", 1.0)
unat.add_element("O", 2.0)
unat.set_density("g/cm3", 10.97)
unat.add_s_alpha_beta("c_O_in_UO2")

light_water = openmc.Material(name = "Light water")
light_water.add_element("H", 2.0)
light_water.add_element("O", 1.0)
light_water.set_density("g/cm3", 1.0)
light_water.add_s_alpha_beta("c_H_in_H2O")

heavy_water = openmc.Material(name = "Heavy water")
heavy_water.add_nuclide("H2", 2.0)
heavy_water.add_element("O", 1.0)
heavy_water.set_density("g/cm3", 1.107)
heavy_water.add_s_alpha_beta("c_D_in_D2O")


graphite = openmc.Material(name = "Graphite")
graphite.add_element("C", 1.0)
graphite.set_density("g/cm3", 1.8)
graphite.add_s_alpha_beta("c_Graphite")

helium = openmc.Material(name = "Helium")
helium.add_element("He", 1.0)
helium.set_density("g/cm3", 0.0001785)

zircaloy = openmc.Material(name = "Zircaloy-4")
zircaloy.add_element("Zr", 0.98335, percent_type = "wo")
zircaloy.add_element("Sn", 0.014, percent_type = "wo")
zircaloy.add_element("Fe", 0.00165, percent_type = "wo")
zircaloy.add_element("Cr", 0.001, percent_type = "wo")
zircaloy.set_density("g/cm3", 6.55)

#----------------------------------------------------------------------------------

# Setter opp boksen og sylinderene våre
#-------------------------------------------------------------------------
box = openmc.model.RectangularPrism(width = 1.4, height = 1.4, boundary_type = "reflective")
z_max = openmc.ZPlane(1, boundary_type = "reflective")
z_min = openmc.ZPlane(-1, boundary_type = "reflective")
inf_cylinder = -openmc.ZCylinder(r = 0.3, boundary_type = "transmission")
sec_cylinder = -openmc.ZCylinder(r = 0.32,  boundary_type = "transmission")
third_cylinder = -openmc.ZCylinder(r = 0.35, boundary_type = "transmission")

#now, just having the 'surfaces'/regions is insufficient, we need to combine them with logic
box_outside_cylinder = -box &+ z_min &- z_max &~ inf_cylinder
volume_cylinder = inf_cylinder &+z_min &-z_max
volsec_cylinder = sec_cylinder &+z_min &-z_max
volthird_cylinder = third_cylinder &+z_min &-z_max
#---------------------------------------------------------------

# Legger inn elementene
#----------------------------------------------------
fuel_cell = openmc.Cell(name = "Fuel")
fuel_cell.fill = unat
fuel_cell.region = volume_cylinder

gass_cell = openmc.Cell(name = "Helium layer")
gass_cell.fill = helium
gass_cell.region = volsec_cylinder

zirc_cell = openmc.Cell(name = "Zircaloy layer")
zirc_cell.fill = zircaloy
zirc_cell.region = volthird_cylinder

mod_cell = openmc.Cell(name = "Moderator")
mod_cell.fill = heavy_water
mod_cell.region = box_outside_cylinder
#--------------------------------------------------------

#setter opp nettene våre:

#-----------------------------------
mesh = openmc.RegularMesh() 
mesh.dimension = [100,100] 
mesh.lower_left= [-0.7,-0.7]
mesh.upper_right= [0.7,0.7] #Making a mesh instance
mesh_filter = openmc.MeshFilter(mesh) #Making a meshfilter

tallies_file = openmc.Tallies() #For our tallies to be included we have to put them into an inp
tally = openmc.Tally(name = "Tally") #Making a tally instance
tally.filters = [mesh_filter] #Designatingen the mesh for the tally
tally.scores = ["flux", 'prompt-nu-fission'] #Designating the objects to be tallied
tallies_file.append(tally) #Appending the tally to our tallies file

#Sette opp energifilteret vår, her går det fra 10^-4 til 10^7
energies = np.logspace(-4,8,501)
energy_filter = openmc.EnergyFilter(energies)
tally2 = openmc.Tally(name = "Energy") 
tally2.filters = [energy_filter] 
tally2.scores = ["flux"]
tallies_file.append(tally2)

tallies_file.export_to_xml()
#--------------------------------------

#setter opp universet
#---------------------------------------------
pin_universe = openmc.Universe(name = "Pincell")
pin_universe.add_cells([fuel_cell, mod_cell,gass_cell, zirc_cell])

materials = openmc.Materials([urox, light_water,zircaloy,helium, heavy_water, graphite,unat])
materials.export_to_xml()

geometry = openmc.Geometry()
geometry.root_universe = pin_universe
geometry.export_to_xml()
#--------------------------------------------

"""
pin_universe.plot(basis = "xy", pixels = [500,500], color_by = "material", colors = {urox: "green", helium: "red",
                                                                                      zircaloy: "black", light_water: "blue"})
plt.title("Pincell top view")

pin_universe.plot(basis = "xz", pixels = [500,500], color_by = "material", colors = {urox: "green", helium: "red", 
                                                                                      zircaloy: "black", light_water: "blue"})
plt.title("Pincell sideview")

plt.show()

"""
#settings ? bare alltid behold
#-------------------------------------
settings = openmc.Settings()

bounds = [-0.7,-0.7,-1,0.7,0.7,1]
uniform_dist = openmc.stats.Box(bounds[:3], bounds[3:],only_fissionable=True)
settings.source = openmc.IndependentSource(space=uniform_dist)

settings.particles = 10000
settings.batches = 100
settings.inactive = 10
settings.export_to_xml()

openmc.run()
#-------------------------------------

