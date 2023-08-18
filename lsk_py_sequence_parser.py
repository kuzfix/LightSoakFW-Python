import json


# How to use:
# pass the config file path to the constructor
# parsing will be done automatically at constructor call
# the parsed command list can be accessed by cmdlist member variable
class LightSoakerSequenceParser:

    def __init__(self, config_file):
        self.config_file = config_file
        self.cmdlist = []
        self.__last_sched_time = 0
        self.parse()


    def parse(self):
        with open(self.config_file) as f:
            config = json.load(f)
        for elem in config['sequence']:
            if 'repeat' in elem and elem['repeat'] > 0:
                for i in range(elem['repeat']):
                    if elem['time_type'] == 'abs':
                        sched_time = elem['time'] * 1000000
                    elif elem['time_type'] == 'rel':
                        sched_time = self.__last_sched_time + elem['time'] * 1000000
                    else:
                        raise Exception('time_type Error')
                    sched_time += i * elem['interval'] * 1000000
                    cmd = f"{elem['cli_cmd']} -sched {sched_time}"
                    cmd += "\n"
                    self.cmdlist.append(cmd)
                self.__last_sched_time = sched_time
            else:
                if elem['time_type'] == 'abs':
                    sched_time = elem['time'] * 1000000
                elif elem['time_type'] == 'rel':
                    sched_time = self.__last_sched_time + elem['time'] * 1000000
                else:
                    raise Exception('time_type Error')
                self.__last_sched_time = sched_time
                cmd = f"{elem['cli_cmd']} -sched {sched_time}"
                cmd += "\n"
                self.cmdlist.append(cmd)

    # print command list to console (for debugging)
    def print_cmdlist(self):
        print(" ## DEBUG: print cmdlist:")
        print("Number of cmds:" , len(self.cmdlist))
        print("###################################")
        for cmd in self.cmdlist:
            print(cmd, end='')
        print("###################################")


# testing
if __name__ == "__main__":
    parser = LightSoakerSequenceParser('test_config.json')
    parser.print_cmdlist()