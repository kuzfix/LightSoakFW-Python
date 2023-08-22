from peewee import *


class LightSoakDatabase:
    def __init__(self, out_dir):
        self.__out_dir = out_dir


    def open_db(self):
        self.db = SqliteDatabase(self.__out_dir + "lightSoakDB.db")

    def create_tables(self):
        self.db.create_tables([Measurement, BufferDump])

    def save_to_db(self, data_dict):
        if(data_dict["type"] == "singlevolt"):
            print("saving single volt")
        elif(data_dict["type"] == "bufferdumpvolt"):
            print("saving dump")


            
        print("saved")







    def close_db(self):
        self.db.close()



class BaseModel(Model):
    class Meta:
        database = SqliteDatabase(None)


class Measurement(BaseModel):
    timestamp = IntegerField()
    ch1 = FloatField(null=True)
    ch2 = FloatField(null=True)
    ch3 = FloatField(null=True)
    ch4 = FloatField(null=True)
    ch5 = FloatField(null=True)
    ch6 = FloatField(null=True)
    DUT_temp = FloatField()
    meas_type = TextField()

class BufferDump(BaseModel):
    timestamp = IntegerField()
    ch1 = FloatField(null=True)
    ch2 = FloatField(null=True)
    ch3 = FloatField(null=True)
    ch4 = FloatField(null=True)
    ch5 = FloatField(null=True)
    ch6 = FloatField(null=True)
    #reference to row from Measurement table
    measurement = ForeignKeyField(Measurement, backref='buffer_dumps')



