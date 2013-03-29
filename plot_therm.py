# coding: utf-8
import yaml
data = yaml.load_all(open("therm_sample.yaml"))

D = [(samp['timestamp'],samp['chan0']) for samp in data]
D = array(D)

V = 3.3*D[:,1]/1024.0
t = D[:,0]
t -= t[0]

plot(t,V)
xlabel("Time (s)")
ylabel("Thermistor Voltage Divider (V)")
title("Hot Water Soil Pour Test")
savefig("hot_water_soil_pour.pdf")
