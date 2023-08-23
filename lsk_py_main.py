import datetime
import time
import lsk_py_hardware_comms
import lsk_py_sequence_parser
import lsk_py_data_in_parser
import lsk_py_temp_control
import lsk_py_database

port = "/dev/cu.usbserial-02B11B94"
# config_file = "test_config.json"
config_file = "config2.json"
output_dir = "output/"



# todo: port as command line argument (also output dir)
# open txt file for general test info


hw = lsk_py_hardware_comms.LightSoakHWComms(port, output_dir, log_all_serial=True)

cnfg = lsk_py_sequence_parser.LightSoakerSequenceParser(config_file)

data = lsk_py_data_in_parser.LightSoakDataInParser(lambda: hw.read_line(), lambda msg: hw.print_hw(msg), output_dir)

db = lsk_py_database.LightSoakDatabase(output_dir)

tempctrl = lsk_py_temp_control.LightSoakTempControl()

db.open_db()

# parse config
cnfg.parse()

# open txt file for general test info
infotxt = open(output_dir + "info_" + cnfg.test_id + ".txt" , "w")

# write general test info to file
infotxt.write(" ### General Test Info ### \n")
now = datetime.datetime.now()
infotxt.write("Time: " + now.strftime("%d-%m-%Y %H:%M:%S") + "\n")
infotxt.write("Test ID: " + cnfg.test_id + "\n")
infotxt.write("Test Notes: " + cnfg.test_notes + "\n")
infotxt.write("DUT Serial: " + cnfg.dut_serial + "\n")
infotxt.write("DUT Target Temp: " + str(cnfg.target_dut_temp) + "\n")
infotxt.write("\n\n")

# write command list to file
infotxt.write(" ### Command List ### \n")
infotxt.write("Number of sequence commands: " + str(len(cnfg.cmdlist)) + "\n")
infotxt.write("########################\n")
for cmd in cnfg.cmdlist:
    infotxt.write(cmd)
infotxt.write("########################\n\n")

# print test duration to file and console
infotxt.write("Estimated total test Duration: " + str(cnfg.test_duration) + "s\n\n")
print("Total test Duration: " + str(cnfg.test_duration) + "s")



#connect to hardware
hw.connect()

# check and report LED temperature at start of test
led_temp = hw.get_led_temp()
infotxt.write("LED Temperature at start of test: " + str(led_temp) + "C\n\n")


# todo: set DUT temperature and wait for it to stabilize

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
        data_dict["DUT_temp"] = tempctrl.get_dut_temp()
        db.save_to_db(data_dict)
        pass
    


#close txt file
infotxt.write(" ### End of Test ### \n")
infotxt.close()

print("end")
raise SystemExit