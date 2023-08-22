from peewee import *

database_proxy = Proxy() # Create a proxy for our db.

class LightSoakDatabase:
    def __init__(self, out_dir):
        self.__out_dir = out_dir


    def open_db(self):
        self.db = SqliteDatabase(self.__out_dir + "lightSoakDB.db")
        database_proxy.initialize(self.db)
        self.__create_tables()

    def __create_tables(self):
        with self.db:
            self.db.create_tables([Measurement, BufferDump])

    def save_to_db(self, data_dict):
        if(data_dict["type"] == "getvolt"):
            meas = Measurement(
                timestamp = data_dict.get("timestamp", None),
                ch1 = data_dict.get("ch1", None),
                ch2 = data_dict.get("ch2", None),
                ch3 = data_dict.get("ch3", None),
                ch4 = data_dict.get("ch4", None),
                ch5 = data_dict.get("ch5", None),
                ch6 = data_dict.get("ch6", None),
                DUT_temp = data_dict.get("DUT_temp", None),
                meas_type = "getvolt"
            )
            meas.save()
            

        elif(data_dict["type"] == "bufferdumpvolt"):
            print("saving dump")

    def close_db(self):
        self.db.close()








# database model classes

class BaseModel(Model):
    class Meta:
        database = database_proxy


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



