"""
Embedded Python Blocks:

Each time this file is saved, GRC will instantiate the first class it finds
to get ports and parameters of your block. The arguments to __init__  will
be the parameters. All of them are required to have default values!
"""
from enum import Enum
import time
import numpy as np
from gnuradio import gr
import tensorflow as tf


class Stage (Enum):
    Scan = 0
    Signal = 1


class blk(gr.sync_block):  # other base classes are basic_block, decim_block, interp_block
    """Embedded Python Block example - a simple multiply const"""

    def __init__(self, vlen=1024, top=None):  # only default arguments here
        """arguments to this function show up as parameters in GRC"""
        gr.sync_block.__init__(
            self,
            name='Spectrum detect',   # will show up in GRC
            in_sig=[(np.float32, vlen), (np.complex64, vlen)],
            out_sig=None
        )
        # if an attribute with the same name as a parameter is found,
        # a callback is registered (properties work, too).
        self.top = top
        self.vlen = vlen
        self.stage = Stage.Scan
        self.startTime = time.time()
        self.model = tf.keras.models.load_model("N_B")

    def work(self, input_items, output_items):
        m = np.amax(input_items[0], 1)
        m_m = max(m)

        print(m_m)
        if self.stage == Stage.Scan:
            if time.time() - self.startTime > 0.3:
                print("Stage:Scan")
                if m_m > 0.01:
                    # self.top.next_channel()
                    # print("detect signal: %10.4f, change channel to: %d" %
                    #   (m_m, self.top.get_cent_fre()))
                    data = []
                    for x in input_items[1]:
                        tem = np.array([y.real for y in x])
                        data.append((tem - tem.min()) /
                                    (tem.max() - tem.min()))
                    data = np.array(data)
                    data.reshape(len(input_items[1]), 1024, 1)
                    prediction = self.model.predict(data)
                    array = [0] * 3
                    for x in prediction:
                        if x[0] > x[1] and x[0] > 0.9:
                            array[0] = array[0] + 1
                        elif x[0] < x[1] and x[1] > 0.9:
                            array[1] = array[1] + 1
                        else:
                            array[2] = array[2] + 1
                    if array[2] != 0:
                        print("Can't analyze the target")
                    elif array[0] > 0:
                        print("It's N210")
                    else:
                        print("It's B200")
                else:
                    print("Don't detect any other user, continue send signal: %d" % (
                        self.top.get_cent_fre()))
                    self.stage = Stage.Signal
                    self.startTime = time.time()
                    self.top.set_amp(1)

        else:
            if time.time() - self.startTime > 0.5:
                print("Stage:Signal")
                self.startTime = time.time()
                self.top.set_amp(0)
                self.stage = Stage.Scan
        self.consume(0, len(input_items[0]))
        self.consume(1, len(input_items[1]))
        return 0
