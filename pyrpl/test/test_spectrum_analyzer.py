import logging
logger = logging.getLogger(name=__name__)
import numpy as np
from time import sleep
from PyQt4 import QtCore, QtGui
from .test_base import TestPyrpl

APP = QtGui.QApplication.instance()

class TestClass(TestPyrpl):

    def test_specan_stopped_at_startup(self):
        """
        This was so hard to detect, I am making a unit test
        """
        assert(self.pyrpl.spectrumanalyzer.running_state=='stopped')

    def test_spec_an(self):
        # at this point this test is still highly dubious (nothing is tested
        #  for, really)
        f0 = 1.1e6
        if self.pyrpl is None:
            return
        sa = self.pyrpl.spectrumanalyzer
        asg = self.pyrpl.rp.asg1
        asg.setup(frequency = f0,
                  amplitude = 0.1,
                  waveform = 'cos',
                  trigger_source = 'immediately')
        sa.setup(center=f0,
                 span=1e3,
                 input=asg)
        curve = sa.curve()
        freqs = sa.frequencies
        fmax = freqs[curve.argmax()]
        diff = np.abs(fmax-f0)
        threshold = float(sa.span)/sa.points
        assert (diff < threshold), (fmax, f0, diff, threshold)
        # TODO: add quantitative test of peak level

    def test_no_write_in_config(self):
        """
        Make sure the spec an isn't continuously writing to config file,
        even in running mode.
        :return:
        """
        self.pyrpl.spectrumanalyzer.setup_attributes = dict(center=2e5,
                                           span=1e5,
                                           input="out1",
                                           running_state='running_continuous')
        for i in range(25):
            sleep(0.01)
            APP.processEvents()
        old = self.pyrpl.c._save_counter
        for i in range(10):
            sleep(0.01)
            APP.processEvents()
        new = self.pyrpl.c._save_counter
        self.pyrpl.spectrumanalyzer.stop()
        assert (old == new), (old, new)
