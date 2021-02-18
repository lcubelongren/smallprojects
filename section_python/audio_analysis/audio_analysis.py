
import numpy as np
import matplotlib.pyplot as plt
import pydub


def read(f, normalized=False):
    """MP3 to numpy array"""
    a = pydub.AudioSegment.from_mp3(f)
    y = np.array(a.get_array_of_samples())
    if a.channels == 2:
        y = y.reshape((-1, 2))
    if normalized:
        return a.frame_rate, np.float32(y) / 2**15
    else:
        return a.frame_rate, y
        

fname = 'Tchaikovsky_Nocturne__orch.mp3'
sr, y = read('sample_mp3s/' + fname)

y = y[10000:11000]
num = np.shape(y)[0]
time = np.linspace(0, num/(sr*60), num)
plt.plot(time, y[:,0], label='left')
plt.plot(time, y[:,1], label='right')
plt.title(fname)
plt.ylabel('amplitude')
plt.xlabel('time [min]')
plt.legend()
plt.show()