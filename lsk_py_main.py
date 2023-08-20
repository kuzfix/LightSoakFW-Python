import lsk_py_hardware_comms
import lsk_py_sequence_parser

port = "/dev/cu.usbserial-02B11B94"
config_file = "test_config.json"


# todo: port as command line argument

#init hardware
hw = lsk_py_hardware_comms.LightSoakHWComms(port)

# load config and test sequence
cnfg = lsk_py_sequence_parser.LightSoakerSequenceParser(config_file)
