

class LightSoakDataInParser:
    def __init__(self, read_line_funct, print_funct, out_dir):
        self.__out_dir = out_dir
        self.__read_line = read_line_funct
        self.__print_hw = print_funct


    
    def test(self):
        self.__print_hw("getvolt -c 1\n")
        while(1):
            line = self.__read_line()
            if(line != None):
                print(line)

    def parse_single_volt(self, data):
        print("parsing volt single")