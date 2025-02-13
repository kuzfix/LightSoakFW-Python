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
import winsound

def exit_handler():
    print("END!")
    #reboot HW (necesary if end of sequence was not reached, otherwise the device resets automatically)
    hw.reboot()
    #time.sleep(1)
    exit()

# atexit.register(exit_handler)
# signal.signal(signal.SIGINT, exit_handler)
# signal.signal(signal.SIGTERM, exit_handler)

def TestInfoLineAdd(str, db, infotxt = None):
    if infotxt is not None:
        infotxt.write(str)
    if db is not None:
        db.add_testinfo_line(str)

def SaveTestInfoToDb(db):
    if db is not None:
        db.save_testinfo()


DBconfig_file = "data/DBconfig.json"
HWconfig_file = "data/HWconfig.json"
output_dir = "data/output/"
#config_file = "data/CalibratePhotodiodesUnderSunSimulator.json"
#config_file = "data/MeasureIllumination(distance).json"
#config_file = "data/config.json"
#config_file = "data/Measure_Isc.json"
#config_file = "data/evaluateLEDresolutionAndStability.json"
#config_file = "data/BasicProtocol.json"
#config_file = "data/ConfigBug01.json"
#config_file = "data/Bug02UnintentionalPause.json"
#config_file = "data/GetIVcurves.json"
#config_file = "data/MPPT.json"
#config_file = "data/Flashmeasure.json"
#config_file = "data/TestProtocol.json"
#config_file = "data/Test.json"
config_file = "data/CyclingVSirradiance.json"

# Check if the directory exists
if os.path.exists(output_dir):
    pass
    """
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
    """
else:
    # Create the directory if it doesn't exist
    os.makedirs(output_dir)



# todo: port as command line argument (also output dir)
# open txt file for general test info




cnfg = lsk_py_sequence_parser.LightSoakerSequenceParser(config_file)
MySQLconnParams = lsk_py_sequence_parser.ParseDBparams(DBconfig_file)
HWcnfg = lsk_py_sequence_parser.ParseHWparams(HWconfig_file)

db = lsk_py_database.LightSoakDatabase(output_dir,MySQLconnParams)


db.open_db()

# parse config
cnfg.parse()

hw = lsk_py_hardware_comms.LightSoakHWComms(HWcnfg['LS_Instrument_Port'], output_dir, log_all_serial=True, buff_size=10e6)

data = lsk_py_data_in_parser.LightSoakDataInParser(lambda: hw.read_line(), lambda msg: hw.print_hw(msg), output_dir)

tempctrl = lsk_py_temp_control.LightSoakTempControl(HWcnfg['Temperature_Ctrl_Port'])

for cfg_idx in range(cnfg.NumConfigs):
    print("****************************")
    print("Running test",cfg_idx+1,"/",cnfg.NumConfigs)
    #Create new measurement sequence in the database
    db.save_meas_sequence(cnfg,cfg_idx,HWcnfg)

    # open txt file for general test info
    #infotxt = open(output_dir + "info.txt" , "w")
    infotxt=None

    # write general test info to file
    TestInfoLineAdd(" ### General Test Info ### \n",db,infotxt)
    now = datetime.datetime.now()
    TestInfoLineAdd("Time: " + now.strftime("%d-%m-%Y %H:%M:%S") + "\n",db,infotxt)
    TestInfoLineAdd("Test ID: " + cnfg.Test_Name[cfg_idx] + "\n",db,infotxt)
    TestInfoLineAdd("Test Notes: " + cnfg.Test_Notes[cfg_idx] + "\n",db,infotxt)
    TestInfoLineAdd("DUT Serial: " + cnfg.DUT_Name[cfg_idx] + "\n",db,infotxt)
    TestInfoLineAdd("DUT Target Temp: " + str(cnfg.DUT_Target_Temperature[cfg_idx]) + "\n",db,infotxt)
    TestInfoLineAdd("HW serial port: " + HWcnfg['LS_Instrument_Port'] + "\n",db,infotxt)
    TestInfoLineAdd("\n\n",None,infotxt)

    # write command list to file
    TestInfoLineAdd(" ### Command List ### \n",db,infotxt)
    TestInfoLineAdd("Number of sequence commands: " + str(len(cnfg.cmdlist[cfg_idx])) + "\n",db,infotxt)
    TestInfoLineAdd("########################\n",db,infotxt)
    for cmd in cnfg.cmdlist[cfg_idx]:
        TestInfoLineAdd(cmd,db,infotxt)
    TestInfoLineAdd("########################\n\n",db,infotxt)

    # print test duration to file and console
    TestInfoLineAdd("Estimated total test Duration: " + str(cnfg.test_duration[cfg_idx]) + "s\n\n",db,infotxt)
    print("Total test Duration: " + str(cnfg.test_duration[cfg_idx]) + "s")



    #connect to hardware
    hw.connect()

    # check and report LED temperature at start of test
    led_temp = hw.get_led_temp()
    TestInfoLineAdd("LED Temperature at start of test: " + str(led_temp) + "C\n\n",db,infotxt)


    if(cnfg.DUT_Target_Temperature[cfg_idx] != "False"):
        # todo: set DUT temperature and wait for it to stabilize
        print("Connecting to temperature controller...")
        tempctrl.connect_to_hw()

        TestInfoLineAdd("DUT Temperature at start of test: " + str(tempctrl.get_dut_temp()) + "C\n\n",db,infotxt)

        # enable temperature control
        print("Enabling temperature control...")
        tempctrl.enable_temp_ctrl()

        print("Setting DUT temperature target...")
        tempctrl.set_dut_temp(cnfg.DUT_Target_Temperature[cfg_idx])
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
        time.sleep(cnfg.DUT_Temp_Settle_Time[cfg_idx])
    else:
        print("No DUT temperature control requested.")

    SaveTestInfoToDb(db)

    try:
        #begin sequence
        hw.sendcmd_reset_timestamp()
        print("!!! Loading & starting sequence !!!")
        eta = datetime.datetime.now() + datetime.timedelta(seconds=cnfg.test_duration[cfg_idx])
        print("ETA: ", eta.strftime('%d-%m-%Y %H:%M:%S'))
        # infotxt.write("ETA: ", eta.strftime('%d-%m-%Y %H:%M:%S'))
        print("Sequence in progress...")

        # send cmds to buffer
        while(True):
            # pop first cmd from list (works like fifo) and try to schedule it
            if(len(cnfg.cmdlist[cfg_idx]) == 0):
                    break
            cmd = cnfg.cmdlist[cfg_idx].pop(0)
            schedok = hw.send_sched_cmd(cmd)
            # if sched fails, we have run out of cmd buffer on HW
            if(schedok == False):
                # if scheduling fails, put cmd back into list and try again later
                cnfg.cmdlist[cfg_idx].insert(0, cmd)
                break

        # run incoming data parser
        while(True):
            try:
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
                        if(len(cnfg.cmdlist[cfg_idx]) == 0):
                            break
                        cmd = cnfg.cmdlist[cfg_idx].pop(0)
                        schedok = hw.send_sched_cmd(cmd)
                        # if sched fails, we have run out of cmd buffer on HW
                        if(schedok == False):
                            # if scheduling fails, put cmd back into list and try again later
                            cnfg.cmdlist[cfg_idx].insert(0, cmd)
                            break
                        break #load only one and wait for new request
                
                if(data_dict != None):
                    # we got some data bois
                    # get dut temperature and save to database

                    # add temperature to data dict
                    if(cnfg.DUT_Target_Temperature[cfg_idx] != "False"):
                        data_dict["DUT_temp"] = tempctrl.get_dut_temp()
                    # for testing purposes, add led temp to data dict
                    # data_dict["ledtemp"] = hw.get_led_temp()

                    # time.sleep(0.1)
                    # for testing purposes, print led temp
                    # print(data_dict.get("ledtemp", None))
                    db.save_to_db(data_dict)
                    pass
            #exit on ctrl+c
            except KeyboardInterrupt:
                print("Keyboard interrupt detected, shutting down and exiting...")
                exit_handler()
            except Exception as e:
                print("Parser exception at " + now.strftime("%d-%m-%Y %H:%M:%S") + "!!! Data may have been missed. Contiuining...")

            

        # disable temperature control 
        if(cnfg.DUT_Target_Temperature[cfg_idx] != "False"):
            #Do not disable temperature control at the end of the measurement. If a light source is still on, we do not want the temperture to run away while idle...
            #print("Disabling temperature control...")
            #tempctrl.disable_temp_ctrl()
            print("Leaving temperature control enabled...")

        print("Sequence complete!")
        winsound.PlaySound("SystemAsterisk",winsound.SND_ALIAS)
        
        TestInfoLineAdd(" ### End of Test ### \n",db,infotxt)
        SaveTestInfoToDb(db)

    except Exception as e:
        print("Exception occured: ", e)
        print("Shutting down and exiting...")
        exit_handler()

#close txt file
if infotxt is not None:
    infotxt.close()

exit_handler()

raise SystemExit


