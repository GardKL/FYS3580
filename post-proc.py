import openmc
import numpy as np
import matplotlib.pyplot as plt


sp = openmc.StatePoint('statepoint.100.h5')
tally = sp.tallies[1]
flux = tally.get_slice(scores=['flux'])
prompt = tally.get_slice(scores=['prompt-nu-fission'])
flux.std_dev.shape = (100, 100)
flux.mean.shape = (100, 100)
prompt.std_dev.shape = (100, 100)
prompt.mean.shape = (100, 100)
fig = plt.subplot(121, title = "Neutron flux distribution")
fig.imshow(flux.mean)
fig2 = plt.subplot(122, title = "Fission site heatmap")
fig2.imshow(prompt.mean)
plt.show()



tally2 = sp.tallies[2]
flx = tally2.mean.ravel()
erange = tally2.filters[0].values
plt.loglog(erange[:-1], flx)
plt.grid()
plt.xlabel("Energy eV")
plt.ylabel("Flux [n/cm-src]")
plt.title("Neutron energy spectrum")
plt.show() #plt.savefig() for heplab
