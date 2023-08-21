import time

class LightSoakDataInParser:
    def __init__(self, read_line_funct, print_funct, out_dir):
        self.__out_dir = out_dir
        self.__read_line = read_line_funct
        self.__print_hw = print_funct
        self.__return_if_no_data_for_s = 3
        
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
                    self.parse_single_volt()


                elif(line == "REQ_SCHED_CMD"):
                    # HW requested new cmds. return to run loop
                    return False




    
    def test(self):
        self.__print_hw("getvolt -c 1\n")
        while(1):
            line = self.__read_line()
            if(line != None and line != ""):
                print(line)

    def parse_single_volt(self):
        print("parsing volt single")
