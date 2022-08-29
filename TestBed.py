#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Testbed
# Author: Zhifan Jiang
# Description: test
# GNU Radio version: 3.10.3.0

from operator import mod
from packaging.version import Version as StrictVersion

if __name__ == '__main__':
    import ctypes
    import sys
    if sys.platform.startswith('linux'):
        try:
            x11 = ctypes.cdll.LoadLibrary('libX11.so')
            x11.XInitThreads()
        except:
            print("Warning: failed to XInitThreads()")

from PyQt5 import Qt
from gnuradio import qtgui
from gnuradio.filter import firdes
import sip
from gnuradio import analog
from gnuradio import blocks
from gnuradio import fft
from gnuradio.fft import window
from gnuradio import gr
import sys
import signal
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
from gnuradio import uhd
import time
import TestBed_epy_block_0 as epy_block_0  # embedded python block


from gnuradio import qtgui


class TestBed(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "Testbed", catch_exceptions=True)
        Qt.QWidget.__init__(self)
        self.setWindowTitle("Testbed")
        qtgui.util.check_set_qss()
        try:
            self.setWindowIcon(Qt.QIcon.fromTheme('gnuradio-grc'))
        except:
            pass
        self.top_scroll_layout = Qt.QVBoxLayout()
        self.setLayout(self.top_scroll_layout)
        self.top_scroll = Qt.QScrollArea()
        self.top_scroll.setFrameStyle(Qt.QFrame.NoFrame)
        self.top_scroll_layout.addWidget(self.top_scroll)
        self.top_scroll.setWidgetResizable(True)
        self.top_widget = Qt.QWidget()
        self.top_scroll.setWidget(self.top_widget)
        self.top_layout = Qt.QVBoxLayout(self.top_widget)
        self.top_grid_layout = Qt.QGridLayout()
        self.top_layout.addLayout(self.top_grid_layout)
        self.current_channel = 0  # 当前所在第几频道

        self.settings = Qt.QSettings("GNU Radio", "TestBed")

        try:
            if StrictVersion(Qt.qVersion()) < StrictVersion("5.0.0"):
                self.restoreGeometry(
                    self.settings.value("geometry").toByteArray())
            else:
                self.restoreGeometry(self.settings.value("geometry"))
        except:
            pass

        ##################################################
        # Variables
        ##################################################
        self.samp_rate = samp_rate = 400000
        self.frequency = frequency = 1000
        self.fft_size = fft_size = 1024
        self.cent_fre = cent_fre = 2.4e9
        self.amp = amp = 0

        ##################################################
        # Blocks
        ##################################################
        self.uhd_usrp_source_1 = uhd.usrp_source(
            ",".join(("addr=192.168.10.6", "")),
            uhd.stream_args(
                cpu_format="fc32",
                args='',
                channels=list(range(0, 1)),
            ),
        )
        self.uhd_usrp_source_1.set_samp_rate(samp_rate)
        # No synchronization enforced.

        self.uhd_usrp_source_1.set_center_freq(cent_fre, 0)
        self.uhd_usrp_source_1.set_antenna("TX/RX", 0)
        self.uhd_usrp_source_1.set_bandwidth(2e7, 0)
        self.uhd_usrp_source_1.set_gain(50, 0)
        self.uhd_usrp_sink_0 = uhd.usrp_sink(
            ",".join(("serial=314FA63", "")),
            uhd.stream_args(
                cpu_format="fc32",
                args='',
                channels=list(range(0, 1)),
            ),
            '',
        )
        self.uhd_usrp_sink_0.set_samp_rate(samp_rate)
        # No synchronization enforced.

        self.uhd_usrp_sink_0.set_center_freq(cent_fre, 0)
        self.uhd_usrp_sink_0.set_antenna('TX/RX', 0)
        self.uhd_usrp_sink_0.set_gain(50, 0)
        self.qtgui_time_sink_x_1 = qtgui.time_sink_c(
            1024,  # size
            samp_rate,  # samp_rate
            "Signal generate",  # name
            1,  # number of inputs
            None  # parent
        )
        self.qtgui_time_sink_x_1.set_update_time(0.10)
        self.qtgui_time_sink_x_1.set_y_axis(-1, 1)

        self.qtgui_time_sink_x_1.set_y_label('Amplitude', "")

        self.qtgui_time_sink_x_1.enable_tags(True)
        self.qtgui_time_sink_x_1.set_trigger_mode(
            qtgui.TRIG_MODE_FREE, qtgui.TRIG_SLOPE_POS, 0.0, 0, 0, "")
        self.qtgui_time_sink_x_1.enable_autoscale(True)
        self.qtgui_time_sink_x_1.enable_grid(False)
        self.qtgui_time_sink_x_1.enable_axis_labels(True)
        self.qtgui_time_sink_x_1.enable_control_panel(True)
        self.qtgui_time_sink_x_1.enable_stem_plot(False)

        labels = ['', '', '', '', '',
                  '', '', '', '', '']
        widths = [1, 1, 1, 1, 1,
                  1, 1, 1, 1, 1]
        colors = ['blue', 'red', 'green', 'black', 'cyan',
                  'magenta', 'yellow', 'dark red', 'dark green', 'dark blue']
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
                  1.0, 1.0, 1.0, 1.0, 1.0]
        styles = [1, 1, 1, 1, 1,
                  1, 1, 1, 1, 1]
        markers = [-1, -1, -1, -1, -1,
                   -1, -1, -1, -1, -1]

        for i in range(2):
            if len(labels[i]) == 0:
                if (i % 2 == 0):
                    self.qtgui_time_sink_x_1.set_line_label(
                        i, "Re{{Data {0}}}".format(i/2))
                else:
                    self.qtgui_time_sink_x_1.set_line_label(
                        i, "Im{{Data {0}}}".format(i/2))
            else:
                self.qtgui_time_sink_x_1.set_line_label(i, labels[i])
            self.qtgui_time_sink_x_1.set_line_width(i, widths[i])
            self.qtgui_time_sink_x_1.set_line_color(i, colors[i])
            self.qtgui_time_sink_x_1.set_line_style(i, styles[i])
            self.qtgui_time_sink_x_1.set_line_marker(i, markers[i])
            self.qtgui_time_sink_x_1.set_line_alpha(i, alphas[i])

        self._qtgui_time_sink_x_1_win = sip.wrapinstance(
            self.qtgui_time_sink_x_1.qwidget(), Qt.QWidget)
        self.top_layout.addWidget(self._qtgui_time_sink_x_1_win)
        self.qtgui_sink_x_0 = qtgui.sink_c(
            1024,  # fftsize
            window.WIN_BLACKMAN_hARRIS,  # wintype
            0,  # fc
            samp_rate,  # bw
            "Signal detect",  # name
            True,  # plotfreq
            True,  # plotwaterfall
            True,  # plottime
            True,  # plotconst
            None  # parent
        )
        self.qtgui_sink_x_0.set_update_time(1.0/10)
        self._qtgui_sink_x_0_win = sip.wrapinstance(
            self.qtgui_sink_x_0.qwidget(), Qt.QWidget)

        self.qtgui_sink_x_0.enable_rf_freq(True)

        self.top_layout.addWidget(self._qtgui_sink_x_0_win)
        self.fft_vxx_0 = fft.fft_vcc(
            fft_size, True, window.blackmanharris(fft_size), True, 1)
        self.epy_block_0 = epy_block_0.blk(vlen=fft_size, top=self)
        self.blocks_stream_to_vector_1 = blocks.stream_to_vector(
            gr.sizeof_gr_complex*1, fft_size)
        self.blocks_complex_to_mag_0 = blocks.complex_to_mag(fft_size)
        self.analog_sig_source_x_0 = analog.sig_source_c(
            samp_rate, analog.GR_COS_WAVE, frequency, amp, 0, 0)

        ##################################################
        # Connections
        ##################################################
        self.connect((self.analog_sig_source_x_0, 0),
                     (self.qtgui_time_sink_x_1, 0))
        self.connect((self.analog_sig_source_x_0, 0),
                     (self.uhd_usrp_sink_0, 0))
        self.connect((self.blocks_complex_to_mag_0, 0), (self.epy_block_0, 0))
        self.connect((self.blocks_stream_to_vector_1, 0),
                     (self.epy_block_0, 1))
        self.connect((self.blocks_stream_to_vector_1, 0), (self.fft_vxx_0, 0))
        self.connect((self.fft_vxx_0, 0), (self.blocks_complex_to_mag_0, 0))
        self.connect((self.uhd_usrp_source_1, 0),
                     (self.blocks_stream_to_vector_1, 0))
        self.connect((self.uhd_usrp_source_1, 0), (self.qtgui_sink_x_0, 0))

    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "TestBed")
        self.settings.setValue("geometry", self.saveGeometry())
        self.stop()
        self.wait()

        event.accept()

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.analog_sig_source_x_0.set_sampling_freq(self.samp_rate)
        self.qtgui_sink_x_0.set_frequency_range(0, self.samp_rate)
        self.qtgui_time_sink_x_1.set_samp_rate(self.samp_rate)
        self.uhd_usrp_sink_0.set_samp_rate(self.samp_rate)
        self.uhd_usrp_source_1.set_samp_rate(self.samp_rate)

    def get_frequency(self):
        return self.frequency

    def set_frequency(self, frequency):
        self.frequency = frequency
        self.analog_sig_source_x_0.set_frequency(self.frequency)

    def get_fft_size(self):
        return self.fft_size

    def set_fft_size(self, fft_size):
        self.fft_size = fft_size
        self.epy_block_0.vlen = self.fft_size

    def get_cent_fre(self):
        return self.cent_fre

    def set_cent_fre(self, cent_fre):
        self.cent_fre = cent_fre
        self.uhd_usrp_sink_0.set_center_freq(self.cent_fre, 0)
        self.uhd_usrp_source_1.set_center_freq(self.cent_fre, 0)

    def get_amp(self):
        return self.amp

    def set_amp(self, amp):
        self.amp = amp
        self.analog_sig_source_x_0.set_amplitude(self.amp)

    def next_channel(self):
        band_width = 20000000
        self.current_channel = current_channel = mod(
            self.current_channel + 1, 7)
        cent_fre = self.cent_fre
        if current_channel == 0:
            cent_fre = cent_fre - 6*band_width
        else:
            cent_fre = cent_fre + band_width
        self.set_cent_fre(cent_fre)


def main(top_block_cls=TestBed, options=None):

    if StrictVersion("4.5.0") <= StrictVersion(Qt.qVersion()) < StrictVersion("5.0.0"):
        style = gr.prefs().get_string('qtgui', 'style', 'raster')
        Qt.QApplication.setGraphicsSystem(style)
    qapp = Qt.QApplication(sys.argv)

    tb = top_block_cls()

    tb.start()

    tb.show()

    def sig_handler(sig=None, frame=None):
        tb.stop()
        tb.wait()

        Qt.QApplication.quit()

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    timer = Qt.QTimer()
    timer.start(500)
    timer.timeout.connect(lambda: None)

    qapp.exec_()


if __name__ == '__main__':
    main()
