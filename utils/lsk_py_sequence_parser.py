import json
import ipaddress


# How to use:
# pass the config file path to the constructor
# call parse() to parse the config file
# the parsed command list can be accessed by cmdlist member variable
# general test parameters can be accessed by member variables
class LightSoakerSequenceParser:

    def __init__(self, config_file):
        self.config_file = config_file
        self.cmdlist = []
        self.test_duration = 0
        self.__seq_begin_deadtime_us = 1000


    def parse(self):
        self.__last_sched_time = 0
        with open(self.config_file) as f:
            config = json.load(f)

        self.User = config['parameters']['User']
        self.Test_Name = config['parameters']['Test_Name']
        self.DUT_Name = config['parameters']['DUT_Name']
        self.DUT_Target_Temperature = config['parameters']['DUT_Target_Temperature']
        self.DUT_Temp_Settle_Time = config['parameters']['DUT_Temp_Settle_Time']
        self.Test_Notes = config['parameters']['Test_Notes']
        self.LS_Instrument_Port = config['parameters']['LS_Instrument_Port']
        self.Temperature_Ctrl_Port = config['parameters']['Temperature_Ctrl_Port']

        for elem in config['sequence']:
            if 'repeat' in elem and elem['repeat'] > 0:
                for i in range(elem['repeat']):
                    if elem['time_type'] == 'abs':
                        sched_time = elem['time'] * 1000000
                        sched_time = int(sched_time) # convert to integer
                    elif elem['time_type'] == 'rel':
                        sched_time = self.__last_sched_time + elem['time'] * 1000000
                        sched_time = int(sched_time) # convert to integer
                    else:
                        raise Exception('time_type Error')
                    sched_time += i * elem['interval'] * 1000000
                    sched_time = int(sched_time) # convert to integer
                    cmd = f"{elem['cli_cmd']} -sched {sched_time}"
                    cmd += "\n"
                    if(sched_time < self.__seq_begin_deadtime_us):
                        raise Exception('Commands scheduled earlier than 10s after sequence begin are not allowed!')
                    self.cmdlist.append(cmd)
                self.__last_sched_time = sched_time
            else:
                if elem['time_type'] == 'abs':
                    sched_time = elem['time'] * 1000000
                    sched_time = int(sched_time) # convert to integer
                elif elem['time_type'] == 'rel':
                    sched_time = self.__last_sched_time + elem['time'] * 1000000
                    sched_time = int(sched_time) # convert to integer
                else:
                    raise Exception('time_type Error')
                self.__last_sched_time = sched_time
                cmd = f"{elem['cli_cmd']} -sched {sched_time}"
                cmd += "\n"
                if(sched_time < self.__seq_begin_deadtime_us):
                        raise Exception('Commands scheduled earlier than 1s after sequence begin are not allowed!')
                self.cmdlist.append(cmd)
        self.test_duration = sched_time / 1000000
        print("JSON config loaded successfully!")
    # print command list to console (for debugging)
    def print_cmdlist(self):
        print(" ## DEBUG: print cmdlist:")
        print("Number of cmds:" , len(self.cmdlist))
        print("###################################")
        for cmd in self.cmdlist:
            print(cmd, end='')
        print("###################################")

# How to use:
# pass the config file path to the function
# return value: dictionary with database connection parameters
#   or None if parameters are obviously invalid
def ParseDBparams(DBconfig_file):
    try:
        with open(DBconfig_file) as f:
            DBconfig = json.load(f)
    except:
        return None

    if not isinstance(DBconfig.get('dbName'),str):
        return None
    if len(DBconfig['dbName'])<1:
        return None
    if not isinstance(DBconfig.get('user'),str):
        return None
    if len(DBconfig['user'])<1:
        return None
    if not isinstance(DBconfig.get('pass'),str):
        return None
    if len(DBconfig['pass'])<1:
        return None
    if not isinstance(DBconfig.get('host'),str):
        return None
    if len(DBconfig['host']) < 7: 
        return None
    if not isinstance(DBconfig.get('port'),int):
        return None
    return DBconfig
    

# testing
if __name__ == "__main__":
    parser = LightSoakerSequenceParser('test_config.json')
    parser.print_cmdlist()