import datetime
import lsk_py_hardware_comms
import lsk_py_sequence_parser
import lsk_py_data_in_parser

port = "/dev/cu.usbserial-02B11B94"
config_file = "test_config.json"
output_dir = "output/"


# todo: port as command line argument (also output dir)
# open txt file for general test info


hw = lsk_py_hardware_comms.LightSoakHWComms(port, output_dir, log_all_serial=True)

cnfg = lsk_py_sequence_parser.LightSoakerSequenceParser(config_file)

data = lsk_py_data_in_parser.LightSoakDataInParser(lambda: hw.read_line(), lambda msg: hw.print_hw(msg), output_dir)

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
infotxt.write("Total test Duration: " + str(cnfg.test_duration) + "s\n\n")
print("Total test Duration: " + str(cnfg.test_duration) + "s")



#connect to hardware
hw.connect()

# check and report LED temperature at start of test
led_temp = hw.get_led_temp()
infotxt.write("LED Temperature at start of test: " + str(led_temp) + "C\n\n")


# todo: set DUT temperature and wait for it to stabilize

#begin sequence


# data.test()
data.parse_single_volt(23)
data.test()





#close txt file
infotxt.write(" ### End of Test ### \n")
infotxt.close()

print("end")
raise SystemExit