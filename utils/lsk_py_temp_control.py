from utils.pyMeCom.mecom import MeCom

# todo: implemnet to interface with TEC controller
class LightSoakTempControl:
    def __init__(self, port):
        self._usb_port = port
        pass

    def connect_to_hw(self):
        if not hasattr(self, '_mc'):
            self._mc = MeCom(self._usb_port)
        self._hw_address = self._mc.identify()
        self._status = self._mc.status()
        print("TEMPCTRL: connected to device: {}, status: {}".format(self._hw_address, self._status))

        #print current temperature to confirm it is working
        temp = self._mc.get_parameter(parameter_name="Object Temperature", address=self._hw_address)
        print("Object temp: {}C".format(temp))
        pass


    def get_dut_temp(self):
        temp = self._mc.get_parameter(parameter_name="Object Temperature", address=self._hw_address)
        return temp
    
    def set_dut_temp(self, temp):
        success = self._mc.set_parameter(value=temp, parameter_id=3000)
        if not success:
            print("TEMPCTRL: failed to set temperature")
            raise Exception("TEMPCTRL: failed to set temperature")
        pass

    def enable_temp_ctrl(self):
        success = self._mc.set_parameter(value=1, parameter_id=2010)
        if not success:
            print("TEMPCTRL: failed to enable temperature control")
            raise Exception("TEMPCTRL: failed to enable temperature control")
        pass
    def disable_temp_ctrl(self):
        success = self._mc.set_parameter(value=0, parameter_id=2010)
        if not success:
            print("TEMPCTRL: failed to disable temperature control")
            raise Exception("TEMPCTRL: failed to disable temperature control")
        pass
    def is_stable(self):
        stable_id = self._mc.get_parameter(parameter_name="Temperature is Stable", address=self._hw_address)
        if stable_id == 2:
            return True
        return False
        