# -*- coding: utf-8 -*-
"""
Parameters and functions specific to the Single frame hyperion sensor

Author: Matthew Dayton (matthew@hcmos.com)

Copyright (c) 2025, Lawrence Livermore National Security, LLC.  All rights reserved.
LLNL-CODE-838080

This work was produced at the Lawrence Livermore National Laboratory (LLNL) under 
contract no. DE-AC52-07NA27344 (Contract 44) between the U.S. Department of Energy (DOE)
and Lawrence Livermore National Security, LLC (LLNS) for the operation of LLNL.
'nsCamera' is distributed under the terms of the MIT license. All new contributions must
be made under this license.

Version: 2.1.2a (August 2025)
"""

from collections import OrderedDict


class hyperion():
    specwarn = ""
    minframe = 0  # fixed value for sensor
    maxframe = 1  # fixed value for sensor
    maxwidth = 512  # fixed value for sensor
    maxheight = 1024  # fixed value for sensor
    bytesperpixel = 2
    icarustype = 0  # 4-frame version
    fpganumID = 1  # last nybble of FPGA_NUM
    detect = "ICARUS_DET"
    sensfam = "Icarus"
    loglabel = "[hyperion] "
    firstframe = 0ƒ
    lastframe = 1
    nframes = 2
    width = 512
    height = 1024
    firstrow = 0
    lastrow = 1023
    interlacing = [0, 0]  # N/A for icarus
    columns = 1
    padToFull = True

    def __init__(self, ca):
        self.ca = ca
        
        # skip board settings if no board object exists
        if hasattr(self.ca, "board"):
            self.init_board_specific()

        (
            self.logcrit,
            self.logerr,
            self.logwarn,
            self.loginfo,
            self.logdebug,
        ) = makeLogLabels(self.ca.logtag, self.loglabel)

        # skip assignment if no comms object exists
        if hasattr(self.ca, "comms"):
            self.ca.comms.payloadsize = (
                self.width * self.height * self.nframes * self.bytesperpixel
            )

        logging.info(self.loginfo + "Initializing sensor object")
        self.sens_registers = OrderedDict(
            {
                "VRESET_WAIT_TIME": "03E",
                "ICARUS_VER_SEL": "041",
                "MISC_SENSOR_CTL": "04C",
                "MANUAL_SHUTTERS_MODE": "050",
                "W0_INTEGRATION": "051",
                "W0_INTERFRAME": "052",
                "W1_INTEGRATION": "053",
                "W1_INTERFRAME": "054",
                "W2_INTEGRATION": "055",
                "W2_INTERFRAME": "056",
                "W3_INTEGRATION": "057",
                "W0_INTEGRATION_B": "058",
                "W0_INTERFRAME_B": "059",
                "W1_INTEGRATION_B": "05A",
                "W1_INTERFRAME_B": "05B",
                "W2_INTEGRATION_B": "05C",
                "W2_INTERFRAME_B": "05D",
                "W3_INTEGRATION_B": "05E",
                "TIME_ROW_DCD": "05F",
            }
        )

        self.sens_subregisters = [
            ## R/W subregs
            # Consistent with ICD usage, start_bit is msb: for [7..0] start_bit is 7
            ("MANSHUT_MODE", "MANUAL_SHUTTERS_MODE", 0, 1, True),
            ("REVREAD", "CTRL_REG", 4, 1, True),
            ("PDBIAS_LOW", "CTRL_REG", 6, 1, True),
            ("ROWDCD_CTL", "CTRL_REG", 7, 1, True),
            ("ACCUMULATION_CTL", "MISC_SENSOR_CTL", 0, 1, True),
            ("HST_TST_ANRST_EN", "MISC_SENSOR_CTL", 1, 1, True),
            ("HST_TST_BNRST_EN", "MISC_SENSOR_CTL", 2, 1, True),
            ("HST_TST_ANRST_IN", "MISC_SENSOR_CTL", 3, 1, True),
            ("HST_TST_BNRST_IN", "MISC_SENSOR_CTL", 4, 1, True),
            ("HST_PXL_RST_EN", "MISC_SENSOR_CTL", 5, 1, True),
            ("HST_CONT_MODE", "MISC_SENSOR_CTL", 6, 1, True),
            ("COL_DCD_EN", "MISC_SENSOR_CTL", 7, 1, True),
            ("COL_READOUT_EN", "MISC_SENSOR_CTL", 8, 1, True),
            ## Read-only subregs
            # Consistent with ICD usage, start_bit is msb: for [7..0] start_bit is 7.
            # WARNING: reading a subregister may clear the entire associated register!
            ("STAT_W3TOPAEDGE1", "STAT_REG", 3, 1, False),
            ("STAT_W3TOPBEDGE1", "STAT_REG", 4, 1, False),
            ("POSID0", "STAT_EDGE_DETECTS", 26, 1, False),#position ID of sensor LSB value
            ("POSID1", "STAT_EDGE_DETECTS", 24, 1, False),#postion ID of sensor MSB value
            ("STAT_HST_ALL_W_EN_DETECTED", "STAT_REG", 12, 1, False),
            ("PDBIAS_UNREADY", "STAT_REG2", 5, 1, False),
        ]

        if self.ca.boardname == "llnl_v4":
            self.sens_subregisters.append(
                ("READOFF_DELAY_EN", "TRIGGER_CTL", 4, 1, True)
            )
            self.sens_registers.update({"DELAY_ASSERTION_ROWDCD_EN": "04F"})

    # TODO: clean up static methods
    def init_board_specific(self): 
        """Initialize aliases and subregisters specific to the current board and sensor.
            Hyperion is designed to work with Icarus V4.0 board"""

        if self.ca.sensorname == "hyperion":
            self.ca.board.subreg_aliases = self.ca.board.icarus_subreg_aliases
            self.ca.board.monitor_controls = self.ca.board.icarus_monitor_controls

    def sensorSpecific(self):
        """
        Returns:
            list of tuples, (Sensor-specific register, default setting)
        """
        return [
            ("ICARUS_VER_SEL", "00000000"),
            ("FPA_FRAME_INITIAL", "00000000"),
            ("FPA_FRAME_FINAL", "00000001"),
            ("FPA_ROW_INITIAL", "00000000"),
            ("FPA_ROW_FINAL", "000003FF"),
            ("HS_TIMING_DATA_BHI", "00000000"),
            ("HS_TIMING_DATA_BLO", "00006666"), # 0db6 = 2-1; 6666 = 2-2
            ("HS_TIMING_DATA_AHI", "00000000"),
            ("HS_TIMING_DATA_ALO", "00006666"),
            #("OSC_SELECT", "11") # Uncomment to enable trigger latch mode as default
            ("FPA_DIVCLK_EN_ADDR", "00000000")  # column Test mode Disabled

        ]

    def getSensTemp(self, scale=None, offset=None, slope=None, dec=None):
        """
        Temperature sensor is embedded in the frames Aout30. This function performs
        a software readout and parses the frames to capture temp sensor voltage
        """
        return 0

    def columnTestEnable(self, val=1):
        control_messages = [("FPA_DIVCLK_EN_ADDR", "00000001")]
        return self.ca.submitMessages(control_messages, " ColumnTestEnable: ")

    def columnTestDisable(self, val=0):
        control_messages = [("FPA_DIVCLK_EN_ADDR", "00000001")]
        return self.ca.submitMessages(control_messages, " ColumnTestDisablee: ")

    def selectTrigLatchEn(self, trig=None):
        """
        Selects Trig Latch Mode to control trigger behaviour. if Trig latch is enabled, 
        then the trigger is latched on rising trigger edge. 
        A trigger latch  reset signal is then reset once the camera is armed and
        the Coarse tigger is sent
        
        Args:
            osc: 'none'|'left'|'right'|'both', defaults to none

        Returns:
            error message as string
        """
        logging.info(self.loginfo + "selectTrigLatchEn; L-R = " + str(trig))
        if trig is None:
            trig = "None"
        trig = str(trig)
        if trig.upper()[:3] == "NON" or "00" in trig:
            payload = "00"
        elif trig.upper()[:3] != "NON" and trig.upper()[:3] != "BOT":
            if "LEF" in trig.upper() or "10" in trig:
                payload = "10"
            if "LEF" in trig.upper() or "01" in trig:
                payload = "01"
        elif trig.lower()[:3] in ["both"] or "11" in trig:
            payload = "11"
        else:
            err = (
                self.logerr + "selectTrigLatchEn: invalid parameter supplied. Try 'none'|'left'|'right'|'both' "
                "TrigLatchEn selection is unchanged."
            )
            logging.error(err)
            return err
        self.ca.setSubregister("OSC_SELECT", payload)

#####
    def setInterlacing(self, ifactor):
        """
        Virtual function; feature is not implemented on Hyperion


        Returns:
            integer 0
        """
        if ifactor:
            logging.warning(
                self.logwarn + "Interlacing is not supported by Hyperion sensors. "
            )
        return 0

    def setHighFullWell(self, flag):
        """
        Virtual function; feature is not implemented on Hyperion
     
        """
        if flag:
            logging.warning(
                self.logwarn + "HighFullWell mode is not supported by Hyperion sensors. "
            )

    def setZeroDeadTime(self, flag):
        """
        Virtual function; feature is not implemented on Hyperion

        """
        if flag:
            logging.warning(
                self.logwarn + "ZeroDeadTime mode is not supported by Hyperion sensors. "
            )

    def setTriggerDelay(self, delay):
        """
        Virtual function; feature is not implemented on Hyperion
  
        """
        if delay:
            logging.warning(
                self.logwarn + "Trigger Delay is not supported by Hyperion sensors. "
            )

    def setPhiDelay(self, delay):
        """
        Virtual function; feature is not implemented on Hyperion

        """
        if delay:
            logging.warning(
                self.logwarn + "Phi Delay is not supported by Hyperion sensors. "
            )

    def setExtClk(self, delay):
        """
        Virtual function; feature is not implemented on Hyperion

        """
        if delay:
            logging.warning(
                self.logwarn + "External Phi Clock is not supported by Hyperion sensors. "
            )


    def setTiming(self, side="AB", sequence=None, delay=0):
         """
        Virtual function; feature is not implemented on Hyperion

        """
        if side:
            logging.warning(
                self.logwarn + "HS Timing is not supported by Hyperion sensors. "
            )
        return 0, 0


    def setArbTiming(self, side="AB", sequence=None):
        """
        Virtual function; feature is not implemented on Hyperion

        """
        if side:
            logging.warning(
                self.logwarn + "HS Timing is not supported by Hyperion sensors. "
            )
        return "", 0


    def getTiming(self, side, actual):
        """
        Virtual function; feature is not implemented on Hyperion

        """
        if side:
            logging.warning(
                self.logwarn + "HS Timing is not supported by Hyperion sensors. "
            )
            return "", 0, 0, 0

    def setManualShutters(self, timing=None):
        """
        Legacy alias for setManualTiming()
        """
        self.setManualTiming(timing)

    def setManualTiming(self, timing=None):
        """
        Virtual function; feature is not implemented on Hyperion
  
        """
        if delay:
            logging.warning(
                self.logwarn + "Manual shutters are not supported by Hyperion sensors. "
            )
        return 0

    def getManualTiming(self):
         """
        Virtual function; feature is not implemented on Hyperion
  
        """
        if delay:
            logging.warning(
                self.logwarn + "Manual shutters are not supported by Hyperion sensors. "
            )
        return [0, 0]


    def selectOscillator(self, osc=None):
        """
        Virtual function; feature is not implemented on Hyperion
  
        """
        if delay:
            logging.warning(
                self.logwarn + "selectOscillators are not supported by Hyperion sensors. "
            )

    def parseReadoff(self, frames, columns):
        """
        Virtual method (Order parsing is unnecessary for hyperion, continue to hemisphere
          parsing.)
        Overridden by Daedalus method
        """
        return self.ca.partition(frames, columns)

    def getSensorStatus(self):
        """
        Wrapper for reportSensorStatus so that the user doesn't have to query statusbits
        """
        sb1 = self.ca.board.checkstatus()
        sb2 = self.ca.board.checkstatus2()
        self.reportStatusSensor(sb1, sb2)

    def reportStatusSensor(self, statusbits, statusbits2):
        """
        Print status messages from sensor-specific bits of status register, default for
          Icarus family sensors
        Args:
            statusbits: result of checkStatus()
            statusbits2: result of checkStatus2()
        """
        if int(statusbits[3]):
            print(self.loginfo + "W3_Top_A_Edge1 detected")
        if int(statusbits[4]):
            print(self.loginfo + "W3_Top_B_Edge1 detected")
        if int(statusbits[12]):
            print(self.loginfo + "HST_All_W_En detected")
        if self.ca.boardname == "llnl_v4" and int(statusbits2[5]):
            print(self.loginfo + "PDBIAS Unready")
"""
Copyright (c) 2025, Lawrence Livermore National Security, LLC.  All rights reserved.  
LLNL-CODE-838080

This work was produced at the Lawrence Livermore National Laboratory (LLNL) under 
contract no. DE-AC52-07NA27344 (Contract 44) between the U.S. Department of Energy (DOE)
and Lawrence Livermore National Security, LLC (LLNS) for the operation of LLNL.
'nsCamera' is distributed under the terms of the MIT license. All new contributions must
be made under this license.
"""
