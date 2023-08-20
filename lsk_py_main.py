import lsk_py_hardware_comms
import lsk_py_sequence_parser

port = "/dev/cu.usbserial-02B11B94"
config_file = "test_config.json"


# todo: port as command line argument

hw = lsk_py_hardware_comms.LightSoakHWComms(port)

cnfg = lsk_py_sequence_parser.LightSoakerSequenceParser(config_file)

# parse config
cnfg.parse()

#connect to hardware
hw.connect()

print("end")
raise SystemExit