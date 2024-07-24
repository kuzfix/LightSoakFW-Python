
# How to add parsing and storing for new data type:
# - Add elif(line == "??" in parser to call a specific parse function
# - implement this specific parser function (return a dict with the data)
# this function must define a new type of the measurement in the dict
# - add elif(data_dict["type"] == "??") in save_to_db function of database class to call a specific save function
# imlpelement this specific save function (save the data to db)
# (if needed, modify database structure in models)




import time
import statistics
from math import isnan

class LightSoakDataInParser:
    def __init__(self, read_line_funct, print_funct, out_dir):
        self.__out_dir = out_dir
        self.__read_line = read_line_funct
        self.__print_hw = print_funct
        
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
                print("Got data: END_OF_SEQUENCE")
                is_end_sequence = True
                is_req_new_cmd = False
                return (None, is_end_sequence, is_req_new_cmd)
            elif(line == "VOLT[V]:"):
                print("Got data: VOLT[V]:")
                data = []
                for i in range(0, 3):
                    data.append(self.__read_line())
                # parse
                data_dict = self.parse_getvolt(data)
                is_end_sequence = False
                is_req_new_cmd = False
                return (data_dict, is_end_sequence, is_req_new_cmd)
            
            elif(line == "CURR[uA]:"):
                print("Got data: CURR[uA]:")
                data = []
                for i in range(0, 3):
                    data.append(self.__read_line())
                # parse
                data_dict = self.parse_getcurr(data)
                is_end_sequence = False
                is_req_new_cmd = False
                return (data_dict, is_end_sequence, is_req_new_cmd)
            
            elif(line == "MPPT[uA__V]:"):
                print("Got data: MPPT[uA__V]:")
                data = []
                for i in range(0, 3):
                    data.append(self.__read_line())
                # parse
                data_dict = self.parse_getMPpoint(data)
                is_end_sequence = False
                is_req_new_cmd = False
                return (data_dict, is_end_sequence, is_req_new_cmd)
            
            elif(line == "IV[uA__V]:"):
                print("Got data: IV[uA__V]:")
                data = []
                for i in range(0, 3):
                    data.append(self.__read_line())
                # parse
                data_dict = self.parse_getivpoint(data)
                is_end_sequence = False
                is_req_new_cmd = False
                return (data_dict, is_end_sequence, is_req_new_cmd)
            
            elif(line == "FLASHMEAS_DUMP:"):
                print("Got data: FLASHMEAS_DUMP:")
                data = []
                while(True):
                    data.append(self.__read_line())
                    if(data[-1] == "END_DUMP"):
                        break
                # parse
                data_dict = self.parse_flashmeasure_dump(data)
                #todo: calculate voltages from dump to have a single voltage reading per channel
                data_dict = self.volt_from_flashdump(data_dict)
                is_end_sequence = False
                is_req_new_cmd = False
                return (data_dict, is_end_sequence, is_req_new_cmd)
            
            elif(line == "DUMPVOLT[V]:"):
                print("Got data: DUMPVOLT[V]:")
                data = []
                while(True):
                    data.append(self.__read_line())
                    if(data[-1] == "END_DUMP"):
                        break
                # parse
                data_dict = self.parse_dumpvolt(data)
                is_end_sequence = False
                is_req_new_cmd = False
                return (data_dict, is_end_sequence, is_req_new_cmd)
            
            elif(line == "DUMPCURR[uA]:"):
                print("Got data: DUMPCURR[uA]:")
                data = []
                while(True):
                    data.append(self.__read_line())
                    if(data[-1] == "END_DUMP"):
                        break
                # parse
                data_dict = self.parse_dumpcurr(data)
                is_end_sequence = False
                is_req_new_cmd = False
                return (data_dict, is_end_sequence, is_req_new_cmd)

            elif(line == "DUMPIVPT[uA__V]:"):
                print("Got data: DUMPIVPT[uA__V]:")
                data = []
                while(True):
                    data.append(self.__read_line())
                    if(data[-1] == "END_DUMP"):
                        break
                # parse
                data_dict = self.parse_dumpiv(data)
                is_end_sequence = False
                is_req_new_cmd = False
                return (data_dict, is_end_sequence, is_req_new_cmd)
            
            elif(line == "IVCHAR[uA__V]:"):
                print("Got data: IVCHAR[uA__V]:")
                data = []
                while(True):
                    data.append(self.__read_line())
                    if(data[-1] == "END_IVCHAR"):
                        break
                # parse
                data_dict = self.parse_getivchar(data)
                is_end_sequence = False
                is_req_new_cmd = False
                return (data_dict, is_end_sequence, is_req_new_cmd)

            elif(line == "LEDTEMP:"):
                print("Got data: LEDTEMP:")
                data = []
                for i in range(0, 2):
                    data.append(self.__read_line())
                # parse
                data_dict = self.parse_getledtemp(data)
                is_end_sequence = False
                is_req_new_cmd = False
                return (data_dict, is_end_sequence, is_req_new_cmd)
            
            elif(line == "RMS_VOLTNOISE[mV]:"):
                print("Got data: RMS_VOLTNOISE[mV]:")
                data = []
                for i in range(0, 3):
                    data.append(self.__read_line())
                # parse
                data_dict = self.parse_getnoisevoltrms(data)
                is_end_sequence = False
                is_req_new_cmd = False
                return (data_dict, is_end_sequence, is_req_new_cmd)
            
            elif(line == "RMS_CURRNOISE[uA]:"):
                print("Got data: RMS_CURRNOISE[uA]:")
                data = []
                for i in range(0, 3):
                    data.append(self.__read_line())
                # parse
                data_dict = self.parse_getnoisecurrrms(data)
                is_end_sequence = False
                is_req_new_cmd = False
                return (data_dict, is_end_sequence, is_req_new_cmd)
            
            elif(line == "SETLEDILLUM:"):
                print("Got data: SETLEDILLUM:")
                data = []
                for i in range(0, 2):
                    data.append(self.__read_line())
                # parse
                data_dict = self.parse_setledillum(data)
                is_end_sequence = False
                is_req_new_cmd = False
                return (data_dict, is_end_sequence, is_req_new_cmd)
            


            elif(line == "REQ_SCHED_CMD"):
                print("Got data: REQ_SCHED_CMD")
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
        # todo: does not handle anything else than 1 or all 6 channels
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

        result_dict["type"] = "getvolt"
        result_dict["timestamp"] = timestamp
        
        if num_channels == 1:
            
            result_dict[f"ch{channel_num}"] = voltages[0]
        else:
            for i, voltage in enumerate(voltages, 1):
                result_dict[f"ch{i}"] = voltage

        return result_dict
    
    def parse_getcurr(self, data_list):
        # todo: does not handle anything else than 1 or all 6 channels
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
        current_data = data_list[2].split(':')
        
        # Validate voltage data
        if num_channels == 1 and len(current_data) != 1:
            raise ValueError("Expected only one voltage reading for one channel.")
        elif num_channels == 6 and len(current_data) != 6:
            raise ValueError("Expected six voltage readings for six channels.")
        
        # Convert the voltage data strings to floats
        currents = [float(v) for v in current_data]

        # Create dictionary to return
        result_dict = {}

        result_dict["type"] = "getcurr"
        result_dict["timestamp"] = timestamp
        
        if num_channels == 1:
            
            result_dict[f"ch{channel_num}_curr"] = currents[0]
        else:
            for i, voltage in enumerate(currents, 1):
                result_dict[f"ch{i}_curr"] = voltage

        return result_dict


 
    def parse_getMPpoint(self, data_list):
        # Ensure there are three elements in the data list
        if len(data_list) != 3:
            raise ValueError("Expected data list to have three elements.")

        # Create dictionary to return
        result_dict = {}
        result_dict["type"] = "mppt"

        # Parse the timestamp
        base_timestamp = int(data_list[0].split(':')[1])
        result_dict["timestamp"] = base_timestamp

        # Get channels from the 2nd line
        channels = [ch.replace('CH','ch') for ch in data_list[1].split(':') if ch.startswith("CH")]

        # Iterate over the sample data lines
        sample_data = data_list[2].split(':')

        # Ensure correct number of samples for channels
        if len(sample_data) != len(channels):
            raise ValueError("Unexpected number of samples for channels.")

        # samples will still be touples with timestamp and value for consistency and code reuse

        # Append samples to respective channel sample lists
        for ch, sample in zip(channels, sample_data):
            curr, volt = map(float, sample.split('_'))
            curr = None if isnan(curr) else curr
            volt = None if isnan(volt) else volt
            result_dict[f"{ch}_curr"] = curr
            result_dict[f"{ch}"] = volt

        return result_dict



    
    def parse_getivpoint(self, data_list):
        # Ensure there are three elements in the data list
        if len(data_list) != 3:
            raise ValueError("Expected data list to have three elements.")

        # Extract the channel number from CHx format
        channel_num = int(data_list[0][2:])

        # Parse the timestamp into an integer
        timestamp = int(data_list[1].split(':')[1])

        # Split current and voltage data using the underscore separator
        curr_data, volt_data = data_list[2].split('_')
        current = float(curr_data)
        voltage = float(volt_data)

        # Create dictionary to return
        result_dict = {}

        result_dict["type"] = "getivpoint"
        result_dict["timestamp"] = timestamp
        result_dict[f"ch{channel_num}_curr"] = current
        result_dict[f"ch{channel_num}"] = voltage

        return result_dict

    def parse_flashmeasure_dump(self, data_list):
        # Check for the type of data
        if (data_list[0] == "DUMPVOLT[V]:"):
            data_list.pop(0) #remove DUMPVOLT[V]: line so data is consistent for parse_dumpvolt
            ret = {}
            ret = self.parse_dumpvolt(data_list)
            ret["type"] = "flashmeasure_dumpvolt"
            return ret
        # if (data_list[0] == "DUMPCURR[uA]:"):
        #     data_list.pop(0) #remove DUMPCURR[uA]: line so data is consistent for parse_dumpcurr
        #     ret = {}
        #     ret = self.parse_dumpcurr(data_list)
        #     ret["type"] = "flashmeasure_dumpcurr"
        #     return ret
        else:
            raise NotImplementedError("This type of data is not implemented yet.")
            # could be flashmeasure_dumpcurrent or flashmeasure_dumpiv for example

        


    
    def parse_dumpvolt(self, data_list):
        # Create dictionary to return
        result_dict = {}
        result_dict["type"] = "dumpvolt"

        # Parse the timestamp
        base_timestamp = int(data_list[0].split(':')[1])
        result_dict["timestamp"] = base_timestamp

        # Parse the sample time
        sampletime = float(data_list[1].split(':')[1])  # Convert to microseconds for integer arithmetic
        sampletime = int(sampletime)
        # Get channels from the 4th line
        channels = data_list[2].split(':')
        num_channels = len(channels)

        # Initialize sample lists for channels
        for ch in channels:
            result_dict[f"{ch}_samples"] = []

        # Iterate over the sample data lines
        samplecnt = 0
        for line_num, line in enumerate(data_list[3:], start=0):
            if line == "END_DUMP":
                break

            # Calculate the sample timestamp
            sample_timestamp = int(base_timestamp + line_num * sampletime)

            # Split the line to get sample data
            sample_data = line.split(']')[1].split(':')

            # Ensure correct number of samples for channels
            if len(sample_data) != num_channels:
                # Fill with -1 to indicate an error
                for ch in channels:
                    result_dict[f"{ch}_samples"].append((sample_timestamp, -1))
                print("parse_dumpvolt: Unexpected number of samples error. Scrapping line and continuing...")
                continue  # Skip the rest of the loop and continue with the next line

            # Append samples to respective channel sample lists
            for ch, sample in zip(channels, sample_data):
                result_dict[f"{ch}_samples"].append((sample_timestamp, float(sample)))
            samplecnt += 1
        result_dict["sample_count"] = samplecnt

        return result_dict 
    
    def parse_dumpcurr(self, data_list):
        # Create dictionary to return
        result_dict = {}
        result_dict["type"] = "dumpcurr"

        # Parse the timestamp
        base_timestamp = int(data_list[0].split(':')[1])
        result_dict["timestamp"] = base_timestamp

        # Parse the sample time
        sampletime = float(data_list[1].split(':')[1])  # Convert to microseconds for integer arithmetic
        sampletime = int(sampletime)
        # Get channels from the 4th line
        channels = data_list[2].split(':')
        num_channels = len(channels)

        # Initialize sample lists for channels
        for ch in channels:
            result_dict[f"{ch}_curr_samples"] = []

        # Iterate over the sample data lines
        samplecnt = 0
        for line_num, line in enumerate(data_list[3:], start=0):
            if line == "END_DUMP":
                break

            # Calculate the sample timestamp
            sample_timestamp = int(base_timestamp + line_num * sampletime)

            # Split the line to get sample data
            sample_data = line.split(']')[1].split(':')

            # Ensure correct number of samples for channels
            if len(sample_data) != num_channels:
                raise ValueError("Unexpected number of samples for channels.")

            # Append samples to respective channel sample lists
            for ch, sample in zip(channels, sample_data):
                result_dict[f"{ch}_curr_samples"].append((sample_timestamp, float(sample)))
            samplecnt += 1
        result_dict["sample_count"] = samplecnt

        return result_dict 
    
    def parse_dumpiv(self, data_list):
        # Create dictionary to return
        result_dict = {}
        result_dict["type"] = "dumpiv"

        # Parse the timestamp
        base_timestamp = int(data_list[0].split(':')[1])
        result_dict["timestamp"] = base_timestamp

        # Parse the sample time
        sampletime = float(data_list[1].split(':')[1])  # Convert to microseconds for integer arithmetic
        sampletime = int(sampletime)
        # Get channels from the 3rd line
        channels = data_list[2].split(':')
        num_channels = len(channels)

        # Initialize sample lists for channels for both current and voltage
        for ch in channels:
            result_dict[f"{ch}_curr_samples"] = []
            result_dict[f"{ch}_samples"] = []

        # Iterate over the sample data lines
        samplecnt = 0
        for line_num, line in enumerate(data_list[3:], start=0):
            if line == "END_DUMP":
                break

            # Calculate the sample timestamp
            sample_timestamp = int(base_timestamp + line_num * sampletime)

            # Split the line to get sample data
            sample_data = line.split(']')[1].split(':')

            # Ensure correct number of samples for channels
            if len(sample_data) != num_channels:
                raise ValueError("Unexpected number of samples for channels.")

            # Append samples to respective channel sample lists
            for ch, sample in zip(channels, sample_data):
                curr, volt = map(float, sample.split('_'))
                result_dict[f"{ch}_curr_samples"].append((sample_timestamp, curr))
                result_dict[f"{ch}_samples"].append((sample_timestamp, volt))
            
            samplecnt += 1

        result_dict["sample_count"] = samplecnt

        return result_dict

    def parse_getivchar(self, data_list):
        # Create dictionary to return
        result_dict = {}
        result_dict["type"] = "getivchar"

        # Parse the timestamp
        base_timestamp = int(data_list[0].split(':')[1])
        result_dict["timestamp"] = base_timestamp

        # Get channels from the 2nd line
        channels = [ch for ch in data_list[1].split(':') if ch.startswith("CH")]
        sample_time = False
        if data_list[1].split(':')[-1] == 't':
            sample_time = True
        num_channels = len(channels) + sample_time

        # Initialize sample lists for channels for both current and voltage
        for ch in channels:
            result_dict[f"{ch}_curr_samples"] = []
            result_dict[f"{ch}_samples"] = []
        
        # Iterate over the sample data lines
        samplecnt = 0
        smpl_t = 0
        for line_num, line in enumerate(data_list[2:], start=0):
            if "NOCONVERGE" in line:
                continue
            if line == "END_IVCHAR":
                break

            # Split the line to get sample data
            if sample_time:
                sample_data = line.split(']')[1].split(':')[:-1]
                smpl_t = int(line.split(']')[1].split(':')[-1])
            else:
                sample_data = line.split(']')[1].split(':')

            # Ensure correct number of samples for channels
            if len(sample_data) != (num_channels-sample_time):
                raise ValueError("Unexpected number of samples for channels.")

            # samples will still be touples with timestamp and value for consistency and code reuse
            # timestam will always be 0 and has no meaning for IV characteristic.

            # Append samples to respective channel sample lists
            for ch, sample in zip(channels, sample_data):
                curr, volt = map(float, sample.split('_'))
                curr = None if isnan(curr) else curr
                volt = None if isnan(volt) else volt
                # result_dict[f"{ch}_curr_samples"].append((0, curr))
                # result_dict[f"{ch}_samples"].append((0, volt))
                result_dict[f"{ch}_curr_samples"].append((smpl_t, curr))
                result_dict[f"{ch}_samples"].append((smpl_t, volt))
            
            samplecnt += 1

        result_dict["sample_count"] = samplecnt

        return result_dict
    
    def parse_getledtemp(self, data_list):
        # Create dictionary to return
        result_dict = {}
        result_dict["type"] = "getledtemp"

        # Parse the timestamp
        base_timestamp = int(data_list[0].split(':')[1])
        result_dict["timestamp"] = base_timestamp

        # Parse the temperature
        temp = float(data_list[1].split(':')[1])

        result_dict["ledtemp"] = temp

        return result_dict
    
    def parse_getnoisevoltrms(self, data_list):
        # todo: does not handle anything else than 1 or all 6 channels
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

        # Parse the noise values based on the number of channels
        noise_data = data_list[2].split(':')
        
        # Validate noise data
        if num_channels == 1 and len(noise_data) != 1:
            raise ValueError("Expected only one voltage reading for one channel.")
        elif num_channels == 6 and len(noise_data) != 6:
            raise ValueError("Expected six voltage readings for six channels.")
        
        # Convert the voltage data strings to floats
        noise_vals = [float(v) for v in noise_data]

        # Create dictionary to return
        result_dict = {}

        result_dict["type"] = "getnoise_volt_rms[mV]"
        result_dict["timestamp"] = timestamp
        
        if num_channels == 1:
            
            result_dict[f"ch{channel_num}"] = noise_vals[0]
        else:
            for i, noise_val in enumerate(noise_vals, 1):
                result_dict[f"ch{i}"] = noise_val

        return result_dict

    def parse_getnoisecurrrms(self, data_list):
        # todo: does not handle anything else than 1 or all 6 channels
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

        # Parse the noise values based on the number of channels
        noise_data = data_list[2].split(':')
        
        # Validate noise data
        if num_channels == 1 and len(noise_data) != 1:
            raise ValueError("Expected only one voltage reading for one channel.")
        elif num_channels == 6 and len(noise_data) != 6:
            raise ValueError("Expected six voltage readings for six channels.")
        
        # Convert the voltage data strings to floats
        noise_vals = [float(v) for v in noise_data]

        # Create dictionary to return
        result_dict = {}

        result_dict["type"] = "getnoise_curr_rms[uA]"
        result_dict["timestamp"] = timestamp
        
        if num_channels == 1:
            
            result_dict[f"ch{channel_num}_curr"] = noise_vals[0]
        else:
            for i, noise_val in enumerate(noise_vals, 1):
                result_dict[f"ch{i}_curr"] = noise_val

        return result_dict


    def parse_setledillum(self, data_list):
        # Create dictionary to return
        result_dict = {}
        result_dict["type"] = "setledillum"

        # Parse the timestamp
        base_timestamp = int(data_list[0].split(':')[1])
        result_dict["timestamp"] = base_timestamp

        # Parse the led illumination
        illum = float(data_list[1].split(':')[1])

        result_dict["ledillum"] = illum

        return result_dict


    


    def volt_from_flashdump(self, data_dict):
        sample_count = data_dict.get("sample_count", 0)
        
        # average center one fifth of the led-on pulse 
        num_avg = int((sample_count-2*200)/5)
        # Calculate the start and end index for the middle 64 samples
        start_idx = (sample_count - num_avg) // 2
        end_idx = start_idx + num_avg
        
        for channel in range(1, 7):  # Loop through channels 1 to 6
            key = f"CH{channel}_samples"
            
            if key in data_dict:  # Check if the channel exists in the data_dict
                # Extract the sample values, disregarding the timestamps
                samples = [sample[1] for sample in data_dict[key][start_idx:end_idx]]
                
                # Calculate the average and standard deviation
                avg = sum(samples) / num_avg
                stdev = statistics.stdev(samples)
                
                # Update the data_dict with the calculated values
                data_dict[f"ch{channel}"] = avg
                data_dict[f"ch{channel}_stdev"] = stdev
                
        return data_dict