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
        is_end_sequence = False
        is_req_new_cmd = False
        data_dict = {}

        while(True):
            line = self.__read_line()
            if(line == ""):
                # no data received, return
                is_end_sequence = False
                is_req_new_cmd = False
                return (None, is_end_sequence, is_req_new_cmd)
            
            # we got data bois
            self.__last_not_empty_time = time.time()
            if(line == "END_OF_SEQUENCE"):
                is_end_sequence = True
                is_req_new_cmd = False
                return (None, is_end_sequence, is_req_new_cmd)
            elif(line == "VOLT[V]:"):
                data = []
                for i in range(0, 3):
                    data.append(self.__read_line())
                # parse
                data_dict = self.parse_getvolt(data)
                is_end_sequence = False
                is_req_new_cmd = False
                return (data_dict, is_end_sequence, is_req_new_cmd)
            
            elif(line == "FLASHMEAS_DUMP:"):
                data = []
                while(True):
                    data.append(self.__read_line())
                    if(data[-1] == "END_DUMP"):
                        break
                # parse
                data_dict = self.parse_flashmeasure_dump(data)
                is_end_sequence = False
                is_req_new_cmd = False
                return (data_dict, is_end_sequence, is_req_new_cmd)

            elif(line == "REQ_SCHED_CMD"):
                # HW requested new cmds. return to run loop
                is_end_sequence = False
                is_req_new_cmd = True
                return (None, is_end_sequence, is_req_new_cmd)
            else:
                # got some data, but nothing we want to parse. run parser loop again
                pass


    
    def test(self):
        self.__print_hw("getvolt -c 1\n")
        while(1):
            line = self.__read_line()
            if(line != None and line != ""):
                print(line)



    def parse_getvolt(self, data_list):
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

        # Create dictionary to return
        result_dict = {}

        if num_channels == 1:
            result_dict["type"] = "getvolt"
            result_dict["timestamp"] = timestamp
            result_dict["ch1"] = voltages[0]
        else:
            result_dict["type"] = "getvolt"
            result_dict["timestamp"] = timestamp
            for i, voltage in enumerate(voltages, 1):
                result_dict[f"ch{i}"] = voltage

        return result_dict
    

    def parse_flashmeasure_dump(self, data_list):
        # Check for the type of data
        if data_list[0] != "DUMPVOLT[V]:":
            raise NotImplementedError("This type of data is not implemented yet.")

        # Create dictionary to return
        result_dict = {}
        result_dict["type"] = "DUMPVOLT"

        # Parse the timestamp
        base_timestamp = int(data_list[1].split(':')[1])
        result_dict["timestamp"] = base_timestamp

        # Parse the sample time
        sampletime = float(data_list[2].split(':')[1])  # Convert to microseconds for integer arithmetic
        sampletime = int(sampletime)
        # Get channels from the 4th line
        channels = data_list[3].split(':')
        num_channels = len(channels)

        # Initialize sample lists for channels
        for ch in channels:
            result_dict[f"{ch}_samples"] = []

        # Iterate over the sample data lines
        for line_num, line in enumerate(data_list[4:], start=0):
            if line == "END_DUMP":
                break

            # Calculate the sample timestamp
            sample_timestamp = int(base_timestamp + line_num * sampletime)

            # Split the line to get sample data
            sample_data = line.split(']')[1][1:].split(':')

            # Ensure correct number of samples for channels
            if len(sample_data) != num_channels:
                raise ValueError("Unexpected number of samples for channels.")

            # Append samples to respective channel sample lists
            for ch, sample in zip(channels, sample_data):
                result_dict[f"{ch}_samples"].append((sample_timestamp, float(sample)))

        return result_dict


    
