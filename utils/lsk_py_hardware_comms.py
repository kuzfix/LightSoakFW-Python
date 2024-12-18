import serial
import datetime
import time

class LightSoakHWComms:
    def __init__(self, ser_port, out_dir, log_all_serial=False, buff_size=None):
        self.__SERIAL_PORT = ser_port
        self.__out_dir = out_dir
        self.__log_all_serial = log_all_serial
        self.__DEFAULT_BAUD = 230400
        self.__FASTAFBOI_BAUD = 2000000
        self.__CONNECT_TIMEOUT = 2
        self.__buff_size=int(buff_size)
        self.__max_buf_utilization = 0

        if(log_all_serial):
            #open file in out_dir names serial_log_<timestamp>.txt
            dt_suffix=datetime.datetime.now().strftime("%Y_%m_%d-%H_%M_%S")
            self.__serial_log = open(out_dir + "serial_log_"+dt_suffix+".txt", "w")
            self.__serial_log.write("Warning: log contains only data that is read by python using read_line. If read_line is not called, data will not be logged! \n")
            self.__serial_log.write(" ### Serial Log ### \n")

    # INIT END ----------------------------------------------------------
    # DESTRUCTOR --------------------------------------------------------
    def __del__(self):
        try:
            self.ser.close()
            print(f"Max recorded RX buffer usage: {self.__max_buf_utilization}/{self.__buff_size}")
        except:
            pass

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
            #self.ser = serial.Serial(self.__SERIAL_PORT, self.__FASTAFBOI_BAUD, timeout=1)
            self.ser.baudrate = self.__FASTAFBOI_BAUD
            self.reboot()
            # baud is now default
            # self.ser = serial.Serial(self.__SERIAL_PORT, self.__DEFAULT_BAUD, timeout=1)
            self.ser.baudrate = self.__DEFAULT_BAUD
            if(not self.__wait_for_ready()):
                raise Exception("LightSoakControl: Unable to connect to lightsoak")

        print("LightSoak HW: Ready")
        print("Changing baud to 2M...")
        self.__set_fastaf_baud()
        if self.__buff_size is not None:
            self.ser.set_buffer_size(rx_size=self.__buff_size)
        self.__max_buf_utilization = 0
        print("LightSoak HW: Configured and ready")
    # MAIN CONNECT FUNCTION END ----------------------------------------------------------

    # READ LINE and PRINT FUNCTION ----------------------------------------------------------
    def read_line(self):
        buf_usage = 0
        try:
            buf_usage = self.ser.in_waiting
            if buf_usage > self.__max_buf_utilization:
                self.__max_buf_utilization = buf_usage
            #debugging...............................
            message = self.ser.readline().decode().strip()
        except UnicodeDecodeError:
            # ignore invalid bytes
            return None
        if(message != ""):
            if(self.__log_all_serial):
                self.__serial_log.write("[" + str(datetime.datetime.now()) + "] " + "IN: " + message + "\n")
        if (buf_usage > self.__buff_size * 0.8):
            print(f"Warning: RX Buffer running low ({buf_usage}/{self.__buff_size})")
        return message

        
    def print_hw(self, message):
        self.ser.write(message.encode())
        if(self.__log_all_serial):
            self.__serial_log.write("[" + str(datetime.datetime.now()) + "] " + "OUT: " + message)
    # READ LINE FUNCTION END ----------------------------------------------------------


    # CONTROL FUNCTIONS FUNCTIONS ----------------------------------------------------------

    def get_timestamp(self):
        self.print_hw("gettimestamp\n")
        while True:
            if self.ser.in_waiting > 0:
                message = self.read_line()
                if message.startswith('TIMESTAMP'):
                    return int(message.split(":")[1])
            time.sleep(0.01)

    def reboot(self):
        self.print_hw("\nreboot\n")

    # sends scheduled CMD and waits for SCHED_OK. returns true if scheduling ok, false if not
    def send_sched_cmd(self, cmd):
        self.print_hw(cmd)
        return self.__wait_for_sched_ok()


    # CONTROL FUNCTIONS FUNCTIONS END ----------------------------------------------------------






    # PRIVATE FUNCTIONS ----------------------------------------------------------
    def __wait_for_ready(self):
        start_time = time.time()
        while True:
            if self.ser.in_waiting > 0:
                try:
                    message = self.read_line()
                except UnicodeDecodeError:
                    # ignore invalid bytes
                    continue
                if message == 'READY':
                    return True
            if time.time() - start_time > self.__CONNECT_TIMEOUT:
                print("Timeout: READY message not received")
                return False

    def __set_fastaf_baud(self):
        self.print_hw("setbaud -b 2000000\n")
        time.sleep(0.1)
        #disconnect and reconnect serial
        self.ser.close()
        self.ser = serial.Serial(self.__SERIAL_PORT, self.__FASTAFBOI_BAUD, timeout=1)
        #send ready?
        self.print_hw("ready?\n")
        self.__wait_for_ready()
        print("Baud changed, ready OK")

    def __wait_for_sched_ok(self):
        start_time = time.time()
        while True:
            if self.ser.in_waiting > 0:
                message = self.read_line()
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
        self.print_hw(cmd)

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
        self.print_hw(cmd)

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
        self.print_hw(cmd)

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
        self.print_hw(cmd)

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
        self.print_hw(cmd)

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
        self.print_hw(cmd)

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
        self.print_hw(cmd)

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
        self.print_hw(cmd)

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
        self.print_hw(cmd)

        if(sched!=False):
            #return true if scheduling ok, false if not
            return self.__wait_for_sched_ok()
        else:
            #return true if cmd is not scheduled
            return True


    def sendcmd_set_led(self, illum_sun):
        cmd = "setledcurr -i " + str(illum_sun) + " \n"
        self.print_hw(cmd)
        #scheduling not supported


    def sendcmd_reset_timestamp(self):
        self.print_hw("resettimestamp\n")

    def get_led_temp(self):
        self.print_hw("getledtemp\n")
        while True:
            if self.ser.in_waiting > 0:
                message = self.read_line()
                if message.startswith('TEMP'):
                    try:
                        Temperature = float(message.split(":")[1])
                    except:
                        Temperature = float("NaN")
                    return Temperature
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