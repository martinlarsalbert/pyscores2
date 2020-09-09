from . import scores1FileParser
import numpy as np
from matplotlib.pylab import *

scores1File = scores1FileParser.Scores1Results(filePath="res207")

spectrum = 0
speeds = list(scores1File.waveSpectras[spectrum].responses.keys())
speed = speeds[0]

waveDirections = []
rolls = []

for waveDirection, responses in sorted(
        scores1File.waveSpectras[spectrum].responses[speed].items()):
    waveDirections.append(waveDirection)
    rolls.append(responses["roll"])

x = np.array(waveDirections)
y = np.array(rolls)

fig = figure()
plot(x, y)

xlabel("Wave direction [deg]")
ylabel("Significant roll [deg]")
title("Result from Scores1")

show()

a = 1
