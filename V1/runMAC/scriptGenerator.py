import numpy as np

print("Welcome to the the macro generator!\n\nWe're here to help you generate your own macrofile for data accumulation!\n")

min = float(input("\tMinimum zpos [mm]: "))
max = float(input("\tMaximum zpos [mm]: "))
N = int(input("\tNumber of trials: "))
part = int(input("\tNumber of photons to Shoot: "))

pos = np.linspace(min,max,N)

file = open("run"+str(min)+"-"+str(max)+"-"+str(N)+"-P"+str(part)+".mac",'w+')

for i in pos:

	filename = "out/%.3f"%(i)
	filename = filename.replace(".","_")+".csv"
	zPos = "%.3f"%(i)
	Nparticles = str(part)

	file.write("#Run %.3f\n/detector/outName "%i+filename+"\n/detector/zpos "+zPos+"\n/run/beamOn "+Nparticles+"\n")

