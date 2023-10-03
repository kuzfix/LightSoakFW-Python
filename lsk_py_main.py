import datetime
import time
import atexit
import signal
import sys
from utils import lsk_py_hardware_comms
from utils import lsk_py_sequence_parser
from utils import lsk_py_data_in_parser
from utils import lsk_py_temp_control
from utils import lsk_py_database
import os
import shutil

def exit_handler():
    print("END!")
    # disable temperature control 
    if(cnfg.target_dut_temp != "False"):
        print("Disabling temperature control...")
        tempctrl.disable_temp_ctrl()
        time.sleep(1)
    #reboot HW
    hw.reboot()
    raise SystemExit

atexit.register(exit_handler)
signal.signal(signal.SIGINT, exit_handler)
signal.signal(signal.SIGTERM, exit_handler)

# config_file = "test_config.json"
config_file = "data/config4.json"
output_dir = "data/output/"

# Check if the directory exists
if os.path.exists(output_dir):
    # Ask the user for their choice
    choice = input(f"'{output_dir}' already exists. Do you want to Continue (C), Erase (E) the folder contents or make a new folder (N)? ").upper()
    
    # If the user chooses 'Erase'
    if choice == 'E':
        # Loop through all files and subdirectories in the directory and remove them
        for filename in os.listdir(output_dir):
            file_path = os.path.join(output_dir, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f"Failed to delete {file_path}. Reason: {e}")
    # If the user chooses 'Continue' (add to database, overwrite info files)
    elif choice == 'C':
        pass
    # If the user chooses 'New' (make a new folder with a timestamp)
    elif choice == 'N':
        # make a new output folder with a timestamp
        now = datetime.datetime.now()
        output_dir = "data/output_" + now.strftime("%Y_%m_%d_%H_%M_%S") + "/"
        os.makedirs(output_dir)
    else:
        print("Invalid choice.")
        raise SystemExit
else:
    # Create the directory if it doesn't exist
    os.makedirs(output_dir)



# todo: port as command line argument (also output dir)
# open txt file for general test info




cnfg = lsk_py_sequence_parser.LightSoakerSequenceParser(config_file)

db = lsk_py_database.LightSoakDatabase(output_dir)


db.open_db()

# parse config
cnfg.parse()

# parse port from config
hw_port = cnfg.hw_port

hw = lsk_py_hardware_comms.LightSoakHWComms(hw_port, output_dir, log_all_serial=True)

data = lsk_py_data_in_parser.LightSoakDataInParser(lambda: hw.read_line(), lambda msg: hw.print_hw(msg), output_dir)

tempctrl = lsk_py_temp_control.LightSoakTempControl(cnfg.temp_ctrl_port)


# open txt file for general test info
infotxt = open(output_dir + "info.txt" , "w")

# write general test info to file
infotxt.write(" ### General Test Info ### \n")
db.save_testinfo_line(" ### General Test Info ### \n")
now = datetime.datetime.now()
infotxt.write("Time: " + now.strftime("%d-%m-%Y %H:%M:%S") + "\n")
db.save_testinfo_line("Time: " + now.strftime("%d-%m-%Y %H:%M:%S") + "\n")
infotxt.write("Test ID: " + cnfg.test_id + "\n")
db.save_testinfo_line("Test ID: " + cnfg.test_id + "\n")
infotxt.write("Test Notes: " + cnfg.test_notes + "\n")
db.save_testinfo_line("Test Notes: " + cnfg.test_notes + "\n")
infotxt.write("DUT Serial: " + cnfg.dut_serial + "\n")
db.save_testinfo_line("DUT Serial: " + cnfg.dut_serial + "\n")
infotxt.write("DUT Target Temp: " + str(cnfg.target_dut_temp) + "\n")
db.save_testinfo_line("DUT Target Temp: " + str(cnfg.target_dut_temp) + "\n")
infotxt.write("HW serial port: " + hw_port + "\n")
db.save_testinfo_line("HW serial port: " + hw_port + "\n")
infotxt.write("\n\n")

# write command list to file
infotxt.write(" ### Command List ### \n")
db.save_testinfo_line(" ### Command List ### \n")
infotxt.write("Number of sequence commands: " + str(len(cnfg.cmdlist)) + "\n")
db.save_testinfo_line("Number of sequence commands: " + str(len(cnfg.cmdlist)) + "\n")
infotxt.write("########################\n")
db.save_testinfo_line("########################\n")
for cmd in cnfg.cmdlist:
    infotxt.write(cmd)
    db.save_testinfo_line(cmd)
infotxt.write("########################\n\n")
db.save_testinfo_line("########################\n\n")

# print test duration to file and console
infotxt.write("Estimated total test Duration: " + str(cnfg.test_duration) + "s\n\n")
db.save_testinfo_line("Estimated total test Duration: " + str(cnfg.test_duration) + "s\n\n")
print("Total test Duration: " + str(cnfg.test_duration) + "s")



#connect to hardware
hw.connect()

# check and report LED temperature at start of test
led_temp = hw.get_led_temp()
infotxt.write("LED Temperature at start of test: " + str(led_temp) + "C\n\n")
db.save_testinfo_line("LED Temperature at start of test: " + str(led_temp) + "C\n\n")


if(cnfg.target_dut_temp != "False"):
    # todo: set DUT temperature and wait for it to stabilize
    print("Connecting to temperature controller...")
    tempctrl.connect_to_hw()

    infotxt.write("DUT Temperature at start of test: " + str(tempctrl.get_dut_temp()) + "C\n\n")
    db.save_testinfo_line("DUT Temperature at start of test: " + str(tempctrl.get_dut_temp()) + "C\n\n")

    # enable temperature control
    print("Enabling temperature control...")
    tempctrl.enable_temp_ctrl()

    print("Setting DUT temperature target...")
    tempctrl.set_dut_temp(cnfg.target_dut_temp)
    time.sleep(0.5)
    # enable temperature control
    print("Enabling temperature control...")
    tempctrl.enable_temp_ctrl()
    time.sleep(0.5)
    print("Waiting for DUT temperature to stabilize...")
    while(tempctrl.is_stable() == False):
        print("Current temperature: ", str(tempctrl.get_dut_temp()), "C")
        time.sleep(2)
    print("Temperature ctrl loop stable! Waiting for additional settling time...")
    time.sleep(cnfg.wait_temp_settle)
else:
    print("No DUT temperature control requested.")

try:
    #begin sequence
    hw.sendcmd_reset_timestamp()
    print("!!! Loading & starting sequence !!!")
    eta = datetime.datetime.now() + datetime.timedelta(seconds=cnfg.test_duration)
    print("ETA: ", eta.strftime('%d-%m-%Y %H:%M:%S'))
    print("Sequence in progress...")

    # send cmds to buffer
    while(True):
        # pop first cmd from list (works like fifo) and try to schedule it
        if(len(cnfg.cmdlist) == 0):
                break
        cmd = cnfg.cmdlist.pop(0)
        schedok = hw.send_sched_cmd(cmd)
        # if sched fails, we have run out of cmd buffer on HW
        if(schedok == False):
            # if scheduling fails, put cmd back into list and try again later
            cnfg.cmdlist.insert(0, cmd)
            break

    # run incoming data parser
    while(True):

        # run parser
        (data_dict, is_end_sequence, is_new_cmd_requested) = data.parser()

        if(is_end_sequence == True):
            #end of sequence, end loop
            break
        if(is_new_cmd_requested == True):
            # cmd loading has priority over saving data, because is time critical
            #  try to load some cmds into buffer
            while(True):
                # pop first cmd from list (works like fifo) and try to schedule it
                if(len(cnfg.cmdlist) == 0):
                    break
                cmd = cnfg.cmdlist.pop(0)
                schedok = hw.send_sched_cmd(cmd)
                # if sched fails, we have run out of cmd buffer on HW
                if(schedok == False):
                    # if scheduling fails, put cmd back into list and try again later
                    cnfg.cmdlist.insert(0, cmd)
                    break
        
        if(data_dict != None):
            # we got some data bois
            # get dut temperature and save to database

            # add temperature to data dict
            if(cnfg.target_dut_temp != "False"):
                data_dict["DUT_temp"] = tempctrl.get_dut_temp()
            # for testing purposes, add led temp to data dict
            # data_dict["ledtemp"] = hw.get_led_temp()

            # time.sleep(0.1)
            # for testing purposes, print led temp
            # print(data_dict.get("ledtemp", None))
            db.save_to_db(data_dict)
            pass
        

    print("Sequence complete!")

    #close txt file
    infotxt.write(" ### End of Test ### \n")
    db.save_testinfo_line(" ### End of Test ### \n")
    infotxt.close()

    exit_handler()

except Exception as e:
    print("Exception occured: ", e)
    print("Shutting down and exiting...")
    exit_handler()


raise SystemExit


