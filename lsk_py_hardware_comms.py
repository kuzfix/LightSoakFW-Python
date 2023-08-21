import serial
import datetime
import time

class LightSoakHWComms:
    def __init__(self, ser_port):
        self.__SERIAL_PORT = ser_port
        self.__DEFAULT_BAUD = 230400
        self.__FASTAFBOI_BAUD = 2000000
        self.__CONNECT_TIMEOUT = 2

    # INIT END ----------------------------------------------------------

    # MAIN CONNECT FUNCTION ----------------------------------------------------------
    def connect(self):
        print("LightSoak HW: Initializing...")
        print("Trying default baud...")
        self.ser = serial.Serial(self.__SERIAL_PORT, self.__DEFAULT_BAUD, timeout=1)
        #reboot so we are in a known state
        print("Rebooting LightSoak...")
        self.reboot()
        # wait for lightsoak to boot
        if(not self.__wait_for_ready()):
            # try with fastafboi baud
            print("Could not connect, trying fast baud...")
            self.ser = serial.Serial(self.__SERIAL_PORT, self.__FASTAFBOI_BAUD, timeout=1)
            self.reboot()
            # baud is now default
            self.ser = serial.Serial(self.__SERIAL_PORT, self.__DEFAULT_BAUD, timeout=1)
            if(not self.__wait_for_ready()):
                raise Exception("LightSoakControl: Unable to connect to lightsoak")

        print("LightSoak HW: Ready")
        print("Changing baud to 2M...")
        self.__set_fastaf_baud()
        print("LightSoak HW: Configured and ready")
    # MAIN CONNECT FUNCTION END ----------------------------------------------------------

    # READ LINE and PRINT FUNCTION ----------------------------------------------------------
    def read_line(self):
        if self.ser.in_waiting > 0:
            try:
                message = self.ser.readline().decode().strip()
            except UnicodeDecodeError:
                # ignore invalid bytes
                return None
            return message
        else:
            return None
        
    def print(self, message):
        self.ser.write(message.encode())
    # READ LINE FUNCTION END ----------------------------------------------------------


    # CONTROL FUNCTIONS FUNCTIONS ----------------------------------------------------------

    def get_timestamp(self):
        self.ser.write("gettimestamp\n".encode())
        while True:
            if self.ser.in_waiting > 0:
                message = self.ser.readline().decode().strip()
                if message.startswith('TIMESTAMP'):
                    return int(message.split(":")[1])
            time.sleep(0.01)

    def reboot(self):
        self.ser.write("reboot\n".encode())


    # CONTROL FUNCTIONS FUNCTIONS END ----------------------------------------------------------






    # PRIVATE FUNCTIONS ----------------------------------------------------------
    def __wait_for_ready(self):
        start_time = time.time()
        while True:
            if self.ser.in_waiting > 0:
                try:
                    message = self.ser.readline().decode().strip()
                except UnicodeDecodeError:
                    # ignore invalid bytes
                    continue
                if message == 'READY':
                    return True
            if time.time() - start_time > self.__CONNECT_TIMEOUT:
                print("Timeout: READY message not received")
                return False

    def __set_fastaf_baud(self):
        self.ser.write("setbaud -b 2000000\n".encode())
        time.sleep(0.1)
        #disconnect and reconnect serial
        self.ser.close()
        self.ser = serial.Serial(self.__SERIAL_PORT, self.__FASTAFBOI_BAUD, timeout=1)
        #send ready?
        self.ser.write("ready?\n".encode())
        self.__wait_for_ready()
        print("Baud changed, ready OK")

    def __wait_for_sched_ok(self):
        start_time = time.time()
        while True:
            if self.ser.in_waiting > 0:
                message = self.ser.readline().decode().strip()
                if message == 'SCHED_OK':
                    return True
                elif message == 'SCHED_FAIL':
                    return False
            if time.time() - start_time > 0.1:
                return False
            time.sleep(0.01)

    # PRIVATE FUNCTIONS END ----------------------------------------------------------



















    # SEND COMMAND FUNCTIONS ----------------------------------------------------------
    # these are obsolete but still usable
    def sendcmd_getvolt(self, channel, sched=False):
        if(channel == "all"):
            cmd = "getvolt\n"
        else:
            cmd = "getvolt -c " + str(channel)
        # scheduled?
        if(sched):
            cmd += " -sched " + str(sched)
        #appen newline
        cmd += " \n"
        # send cmd
        self.ser.write(cmd.encode())

        if(sched!=False):
            #return true if scheduling ok, false if not
            return self.__wait_for_sched_ok()
        else:
            #return true if cmd is not scheduled
            return True
        

    def sendcmd_getcurr(self, channel, sched=False):
        if(channel == "all"):
            cmd = "getcurr\n"
        else:
            cmd = "getcurr -c " + str(channel)
        # scheduled?
        if(sched):
            cmd += " -sched " + str(sched)
        #appen newline
        cmd += " \n"
        # send cmd
        self.ser.write(cmd.encode())

        if(sched!=False):
            #return true if scheduling ok, false if not
            return self.__wait_for_sched_ok()
        else:
            #return true if cmd is not scheduled
            return True


    def sendcmd_getiv_point(self, channel, voltage, sched=False):
        if(channel == "all"):
            raise Exception("LightSoakControl: Cannot get iv point for all channels")
        else:
            cmd = "getivpoint -c " + str(channel) + " -v " + str(voltage)
        # scheduled?
        if(sched):
            cmd += " -sched " + str(sched)
        #appen newline
        cmd += " \n"
        # send cmd
        self.ser.write(cmd.encode())

        if(sched!=False):
            #return true if scheduling ok, false if not
            return self.__wait_for_sched_ok()
        else:
            #return true if cmd is not scheduled
            return True


    def sendcmd_getiv_char(self, channel, v_start, v_stop, v_step, sched=False):
        if(channel == "all"):
            raise Exception("LightSoakControl: Cannot get iv point for all channels")
        else:
            cmd ="getivchar -c " + str(channel) + " -vs " + str(v_start) + " -ve " + str(v_stop) + " -s " + str(v_step)
        # scheduled?
        if(sched):
            cmd += " -sched " + str(sched)
        #appen newline
        cmd += " \n"
        # send cmd
        self.ser.write(cmd.encode())

        if(sched!=False):
            #return true if scheduling ok, false if not
            return self.__wait_for_sched_ok()
        else:
            #return true if cmd is not scheduled
            return True
        

    def sendcmd_dump_voltage(self, channel, num_samples, sched=False):
        if(channel == "all"):
            cmd = "measuredump -n " + str(num_samples) + " -VOLT"
        else:
            cmd = "measuredump -c " + str(channel) + " -n " + str(num_samples) + " -VOLT"

        # scheduled?
        if(sched):
            cmd += " -sched " + str(sched)
        #appen newline
        cmd += " \n"
        # send cmd
        self.ser.write(cmd.encode())

        if(sched!=False):
            #return true if scheduling ok, false if not
            return self.__wait_for_sched_ok()
        else:
            #return true if cmd is not scheduled
            return True
        

    def sendcmd_dump_current(self, channel, num_samples, sched=False):
        if(channel == "all"):
            cmd = "measuredump -n " + str(num_samples) + " -CURR"
        else:
            cmd = "measuredump -c " + str(channel) + " -n " + str(num_samples) + " -CURR"

        # scheduled?
        if(sched):
            cmd += " -sched " + str(sched)
        #appen newline
        cmd += " \n"
        # send cmd
        self.ser.write(cmd.encode())

        if(sched!=False):
            #return true if scheduling ok, false if not
            return self.__wait_for_sched_ok()
        else:
            #return true if cmd is not scheduled
            return True
        

    def sendcmd_dump_iv(self, channel, num_samples, sched=False):
        if(channel == "all"):
            cmd = "measuredump -n " + str(num_samples) + " -IV"
        else:
            cmd = "measuredump -c " + str(channel) + " -n " + str(num_samples) + " -IV"

        # scheduled?
        if(sched):
            cmd += " -sched " + str(sched)
        #appen newline
        cmd += " \n"
        # send cmd
        self.ser.write(cmd.encode())

        if(sched!=False):
            #return true if scheduling ok, false if not
            return self.__wait_for_sched_ok()
        else:
            #return true if cmd is not scheduled
            return True


    def sendcmd_flashmeasure_singlesample(self, channel, illum, flash_dur, smpl_at, num_avg, sched=False):
        if(channel == "all"):
            cmd = "flashmeasure -n " + str(num_avg) + " -illum " + str(illum) + " -m " + str(smpl_at) + " -t " + str(flash_dur)
        else:
            cmd = "flashmeasure -c " + str(channel) + " -n " + str(num_avg) + " -illum " + str(illum) + " -m " + str(smpl_at) + " -t " + str(flash_dur)

        # scheduled?
        if(sched):
            cmd += " -sched " + str(sched)
        #appen newline
        cmd += " \n"
        # send cmd
        self.ser.write(cmd.encode())

        if(sched!=False):
            #return true if scheduling ok, false if not
            return self.__wait_for_sched_ok()
        else:
            #return true if cmd is not scheduled
            return True
        

    def sendcmd_flashmeasure_dump(self, channel, illum, flash_dur, sched=False):
        if(channel == "all"):
            cmd = "flashmeasure" + " -illum " + str(illum) + " -t " + str(flash_dur) + " -DUMP"
        else:
            cmd = "flashmeasure -c " + str(channel) + " -illum " + str(illum) + " -t " + str(flash_dur) + " -DUMP"

        # scheduled?
        if(sched):
            cmd += " -sched " + str(sched)
        #appen newline
        cmd += " \n"
        # send cmd
        self.ser.write(cmd.encode())

        if(sched!=False):
            #return true if scheduling ok, false if not
            return self.__wait_for_sched_ok()
        else:
            #return true if cmd is not scheduled
            return True


    def sendcmd_set_led(self, illum_sun):
        cmd = "setledcurr -i " + str(illum_sun) + " \n"
        self.ser.write(cmd.encode())
        #scheduling not supported


    def sendcmd_reset_timestamp(self):
        self.ser.write("resettimestamp\n".encode())

    def get_led_temp(self):
        self.ser.write("getledtemp\n".encode())
        while True:
            if self.ser.in_waiting > 0:
                message = self.ser.readline().decode().strip()
                if message.startswith('LEDTEMP'):
                    return float(message.split(":")[1])
            time.sleep(0.01)

    # SEND COMMAND FUNCTIONS END ----------------------------------------------------------



    







if __name__ == '__main__':
    lsk = LightSoakHWComms("/dev/cu.usbserial-02B11B94")
    lsk.connect()
    time.sleep(1)
    # lsk.sendcmd_getvolt(1, sched=10000000)
    # lsk.sendcmd_getcurr(1)
    # lsk.sendcmd_getiv_point(1, 0.5)
    # lsk.sendcmd_getiv_char(1, 0.0, 0.3, 0.01)
    # lsk.sendcmd_dump_iv("all", 10)
    # lsk.sendcmd_flashmeasure_dump("all", 0.8, 100, sched=10000000)
    # lsk.sendcmd_set_led(0.8)

    print(lsk.get_timestamp())
    lsk.sendcmd_reset_timestamp()
    time.sleep(1)
    print(lsk.get_timestamp())


    # print incoming lines
    timeout = 20  # set timeout to 10 seconds
    last_message_time = time.time()  # initialize last message time
    while True:
        if lsk.ser.in_waiting > 0:
            try:
                message = lsk.ser.readline().decode().strip()
            except UnicodeDecodeError:
                # ignore invalid bytes
                continue
            print(message)
            last_message_time = time.time()  # update last message time
        if time.time() - last_message_time > timeout:
            break  # stop the loop if no message received for 10 seconds
        # time.sleep(0.01)


    #stop python script
    raise Exception("LightSoakControl: Exiting")    