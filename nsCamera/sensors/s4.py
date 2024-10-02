# -*- coding: utf-8 -*-
"""
Parameters and functions specific to the S4 sensor

Author: Matthew Dayton (matthew@hcmos.com)

Version: 2.2.1  (July 2024)
"""

import itertools
import logging
import numpy as np
from collections import OrderedDict


class s4:
    def __init__(self, camassem):
        self.ca = camassem
        self.logcrit = self.ca.logcritbase + "[S4] "
        self.logerr = self.ca.logerrbase + "[S4] "
        self.logwarn = self.ca.logwarnbase + "[S4] "
        self.loginfo = self.ca.loginfobase + "[S4] "
        self.logdebug = self.ca.logdebugbase + "[S4] "
        logging.info(self.loginfo + "initializing sensor object")
        self.minframe = 0
        self.maxframe = 1
        self.firstframe = self.minframe
        self.lastframe = self.maxframe
        self.nframes = self.maxframe - self.minframe + 1
        self.maxwidth = 512
        self.maxheight = 1024
        self.firstrow = 0
        self.lastrow = self.maxheight - 1
        self.width = self.maxwidth
        self.height = self.maxheight
        self.bytesperpixel = 2
        self.icarustype = 0  # 4-frame version
        self.fpganumID = "1"  # last nybble of FPGA_NUM
        self.interlacing = 0


        self.sens_registers = OrderedDict(
            {
                "VRESET_WAIT_TIME": "03E",
                "S4_VER_SEL": "041",
                "MISC_SENSOR_CTL": "04C",
                "TIME_ROW_DCD": "05F",
                "NCOLTSTEN": "046",
            }
        )

        self.sens_subregisters = [
            ("STAT_W3TOPLEDGE1", "STAT_REG", 3, 1, False),
            ("STAT_W3TOPREDGE1", "STAT_REG", 4, 1, False),
            ("REVREAD", "CTRL_REG", 4, 1, True),
            ("PDBIAS_UNREADY", "STAT_REG2", 5, 1, False),
            ("PDBIAS_LOW", "CTRL_REG", 6, 1, True),
            ("ROWDCD_CTL", "CTRL_REG", 7, 1, True),
            ("HST_PXL_RST_EN", "MISC_SENSOR_CTL", 5, 1, True),
            ("COL_DCD_EN", "MISC_SENSOR_CTL", 7, 1, True),
            ("BIASEN", "MISC_SENSOR_CTL", 8, 1, True),
            ("RDCDEN", "FPA_OSCILLATOR_SEL_ADDR", 0, 1, True),#may need to try bit pos 1 instead?
        ]

    def checkSensorVoltStat(self):
        """
        Checks register tied to sensor select jumpers to confirm match with sensor
        object

        Returns:
            boolean, True if jumpers select for S4 sensor
        """
        err, status = self.ca.getSubregister("S4_DET")
        if err:
            logging.error(self.logerr + "unable to confirm sensor status")
            return False
        if not int(status):
            logging.error(self.logerr + "S4 sensor not detected")
            return False
        return True

    def sensorSpecific(self):
        """
        Returns:
            list of tuples, (Sensor-specific register, default setting)
        """
        return [
            ("S4_VER_SEL", "00005334"),
            ("FPA_FRAME_INITIAL", "00000000"),
            ("FPA_FRAME_FINAL", "00000003"),
            ("FPA_ROW_INITIAL", "00000000"),
            ("FPA_ROW_FINAL", "000003FF")
        ]

    def setInterlacing(self, ifactor):
        """
        Dummy function; feature is not implemented on S4

        Returns:
            integer 1
        """
        if ifactor:
            logging.warning(
                self.logwarn + "Interlacing is not supported by the S4 sensor."
            )
        return 1

    def setHighFullWell(self, flag):
        """
        Dummy function; feature is not implemented on S4
        """
        if flag:
            logging.warning(
                self.logwarn + "HighFullWell mode is not supported by the S4 "
                "sensor. "
            )

    def setZeroDeadTime(self, flag):
        """
        Dummy function; feature is not implemented on S4
        """
        if flag:
            logging.warning(
                self.logwarn + "ZeroDeadTime mode is not supported by the S4 "
                "sensor. "
            )

    def setTriggerDelay(self, delayblocks):
        """
        Dummy function; feature is not implemented on S4
        """
        if delayblocks:
            logging.warning(
                self.logwarn + "Trigger Delay is not supported by the S4 "
                "sensor. "
            )

    def setTiming(self, side, sequence, delay):
        """
        Timing registers not implemented in S4
        """
        if side:
            logging.warning(
                self.logwarn + "Timing registers is not supported by the S4 "
                "sensor. "
            )
        return ""

    def setArbTiming(self, side, sequence):
        """
        Timing registers not implemented in S4
        """
        if side:
            logging.warning(
                self.logwarn + "Timing registers is not supported by the S4 "
                "sensor. "
            )
        return ""

    def getTiming(self, side, actual):
        """
        Timing registers not implemented in S4
        """
        if side:
            logging.warning(
                self.logwarn + "Timing registers is not supported by the S4 "
                "sensor. "
            )
        return ""

    def setManualShutters(self, timing):
        """
        Timing registers not implemented in S4
        """
        if side:
            logging.warning(
                self.logwarn + "Timing registers is not supported by the S4 "
                "sensor. "
            )
        return ""

    def getManualTiming(self):
        """
        Timing registers not implemented in S4
        """
        if side:
            logging.warning(
                self.logwarn + "Timing registers is not supported by the S4 "
                "sensor. "
            )
        return ""

    def parseReadoff(self, frames):
        """
        Parse Frames for single frame S4 sensor. Although each S4 readout slice is 64 columns wide 
        instead of 32 like icarus. The Frame1 signal is used for Column Decode 5 signal.
        """
        def interlace_arrays(array1, array2):
            # Ensure the arrays have the correct shape
            #array1 = array1[0:1024,0:512] #crop out any column padding
            #array2 = array2[0:1024,0:512] #crop out any column padding
            assert array1.shape == (1024, 512), f"array1 must be of shape (1024, 512), found {np.shape(array1)}"
            assert array2.shape == (1024, 512), f"array2 must be of shape (1024, 512), found {np.shape(array2)}"
            
            # Split both arrays into groups of 32 columns
            groups1 = np.split(array1, 16, axis=1)  # List of 16 arrays of shape (1024, 32)
            groups2 = np.split(array2, 16, axis=1)  # List of 16 arrays of shape (1024, 32)
            
            # Interlace the groups
            interlaced_groups = []
            for g1, g2 in zip(groups1, groups2):
                interlaced_groups.append(g1)
                interlaced_groups.append(g2)
            
            # Concatenate the interlaced groups along the column axis
            interlaced_array = np.concatenate(interlaced_groups, axis=1)
            
            return interlaced_array

        s4_frames = []
        frames = np.reshape(frames,(self.nframes,self.height,self.width))
        # Iterate two elements at a time
        for first, second in zip(frames[::2], frames[1::2]):
            s4_frames.append(interlace_arrays(first, second)) 
        s4_frames_2d = np.array(s4_frames)
        #s4_row_groups = np.split(s4_frames_2d[0], 4, axis=0)
        #s4_frames = np.concatenate((np.concatenate(s4_row_groups[::2],axis=0), np.concatenate(s4_row_groups[1::2],axis=0)),axis=0)
        #s4_frames_2d = np.array(s4_frames)
        s4_frames_1d = s4_frames_2d.reshape((self.height,2*self.width))
        return s4_frames_1d.astype(np.int32)

    def reportStatusSensor(self, statusbits):
        """
        Print status messages from sensor-specific bits of status register

        Args:
            statusbits: result of checkStatus()
        """
        err, rval = self.ca.getRegister("STAT_EDGE_DETECTS")
        # shift to left to fake missing edge detect
        edgebits = bin(int(rval, 16) << 1)[2:].zfill(32)
        # reverse to get order matching assignment
        bitsrev = edgebits[::-1]
        cross_reference = {
            "TCACCESINBYPASS": "W0_BOT_L_EDGE2",
            "BGTRIMA0": "W2_BOT_L_EDGE2",
            "BGTRIMA1": "W2_BOT_L_EDGE1",
            "BGTRIMA2": "W1_BOT_L_EDGE2",
            "BGTRB0": "W1_TOP_L_EDGE2",
            "BGTRB1": "W2_TOP_L_EDGE1",
            "BGTRB2": "W2_TOP_L_EDGE2",
            "BGTRB3": "W3_TOP_L_EDGE1",
            "TC_SHIF_IN_UP": "W3_BOT_R_EDGE1",
            "TC_GLB_CHARGE_EN": "W2_BOT_R_EDGE1",
            "TC_DC_PXL_ACCESS_EN": "W2_BOT_R_EDGE2",
            "TCnDCPXLACCOUT": "W0_BOT_R_EDGE1",
            "TC_SR_PRGM_MODE": "W3_BOT_R_EDGE2",
            "TCSRUPOUT": "W1_BOT_R_EDGE1",
            "TCSRDNOUT": "W1_BOT_R_EDGE2",
            "TC_SHIFT_IN_DN": "W3_TOP_R_EDGE1",
            "TC_nRST_SR": "W3_TOP_R_EDGE2",
            "TC_TEST_AMP_EN": "W2_TOP_R_EDGE1",
            "TRGOUT": "W0_TOP_R_EDGE1",
            "TRGIN": "W0_TOP_R_EDGE2", 
            "REPTREEOUT": "W0_TOP_L_EDGE1",
            "TC_TEST_CLK_IN": "W2_TOP_R_EDGE2"
        }
        detdict = {}
        for frame in range(4):
            for vert in ("TOP", "BOT"):
                for edge in range(1, 3):
                    for hor in ("L", "R"):
                        detname = (
                            "W" + str(frame) + "_" + vert + "_" + hor + "_EDGE" + str(edge)
                        )
                        detdict[detname] = bitsrev[bitidx]
                        bitidx += 1
        # Initialize an empty dictionary to store the results with integer values
        result_dict = {}

        # Map each label to its corresponding integer index
        for label, key in cross_reference.items():
            if key in detdict:
                # Get the index of the corresponding bit in the bitsrev array
                bit_value = bitsrev.index(detdict[key])
                result_dict[label] = bit_value
                if int(bit_value):
                    logging.info(self.loginfo + label + " Detected")
            else:
                result_dict[label] = None  # Handle cases where the key is not found

        return result_dict
