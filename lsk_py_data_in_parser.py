import time

class LightSoakDataInParser:
    def __init__(self, read_line_funct, print_funct, out_dir):
        self.__out_dir = out_dir
        self.__read_line = read_line_funct
        self.__print_hw = print_funct
        self.__return_if_no_data_for_s = 3
        
    #todo: rewrite so it parses one set of data and return a touple: (data_dict, is_end_of_sequence, is_new_cmd_requested)
    # returns True if end of sequence is reached - END_OF_SEQUENCE received from hw
    def parser(self):
        self.__last_not_empty_time = time.time()
        while(True):
            line = self.__read_line()
            if(line == "" or line == None):
                if(time.time() - self.__last_not_empty_time > self.__return_if_no_data_for_s):
                    # print("no cmd for 3s")
                    # return False
                    pass
            else:
                # we got data bois
                self.__last_not_empty_time = time.time()
                if(line == "END_OF_SEQUENCE"):
                    return True
                elif(line == "VOLT[V]:"):
                    data = []
                    for i in range(0, 3):
                        data.append(self.__read_line())
                    self.parse_single_volt(data)


                elif(line == "REQ_SCHED_CMD"):
                    # HW requested new cmds. return to run loop
                    return False





    
    def test(self):
        self.__print_hw("getvolt -c 1\n")
        while(1):
            line = self.__read_line()
            if(line != None and line != ""):
                print(line)

    def parse_single_volt(self, data_list):
        # Ensure there are three elements in the data list
        if len(data_list) != 3:
            raise ValueError("Expected data list to have three elements.")

        # Split the channel data string
        channel_data = data_list[0].split(':')

        # Check the number of channels based on the channel data length
        if len(channel_data) == 1:
            num_channels = 1
            channel_num = int(channel_data[0][2:])  # Extract the channel number from CHx
        elif len(channel_data) == 6:
            num_channels = 6
        else:
            raise ValueError("Unexpected number of channels.")

        # Parse the timestamp into an integer
        timestamp = int(data_list[1].split(':')[1])

        # Parse the voltages based on the number of channels
        voltage_data = data_list[2].split(':')
        
        # Validate voltage data
        if num_channels == 1 and len(voltage_data) != 1:
            raise ValueError("Expected only one voltage reading for one channel.")
        elif num_channels == 6 and len(voltage_data) != 6:
            raise ValueError("Expected six voltage readings for six channels.")
        
        # Convert the voltage data strings to floats
        voltages = [float(v) for v in voltage_data]

        # Output based on the number of channels
        if num_channels == 1:
            print(f"Channel: {channel_num}\nTimestamp: {timestamp}\nVoltage: {voltages[0]}")
        else:
            print(f"Channels: {list(range(1, 7))}\nTimestamp: {timestamp}\nVoltages: {voltages}")
    
