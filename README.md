# LightSoak Python Data Logger
This code is a Python data logger to be used with the LightSoak Hardware: https://github.com/mrmp17/LightSoakFW-STM. It implements data logging to a database, specialized for light soaking measurements for perovskite solar cell samples. This was developed as a part of my Masters thesis.

## Quick start quide
> First, get familiar with standalone use of the LighSoak hardware. Programming measurement sequences follows the same practices as standalone use. Follow https://github.com/mrmp17/LightSoakFW-STM for directions.

> Required libraries: pySerial, Peewee

> Recomended database browser: DB browser for SQLite

### File structure
- *Root directory*
    - *lsk_py_main.py* (main Python script)
    - *utils*
        - *Other helper Python modules*
    - *data*
        - *config.json*
        - *output*
            - *info.txt*
            - *LightSoakDB.db*
            - *serial_log.txt*

*data* folder is where all the configuration and output files are. *info.txt* contains various test parameters and conditions and the generated command list. This data is also saved to database in *testinfo* table. *LightSoakDB.db* is the SQLite database. *serial_log.txt* logs all sent and received data to and from hardware.

If *output* folder is not present when the code is run, it will be created. If It does exist, user will be prompted to select on of three actions:
- keep the folder, but overwrite *info.txt* and *serial_log.txt* and append data to the database
- erase the folder contents completely
- create a new output folder

### Test configuration
Test configuration and sequence is defined in *config.json*.

In *parameters* section, user can define test parameter and some general information to be logged into *info.txt*. Importantly, the serial port is defined here. Target temperature for DUT temperature control is also specified here. If no temperature control should be used, set *DUT_target_temperature* to *"False"*. Parameter *DUT_wait_temp_settle* is used to specify waiting time after temperature controller reports stable control loop. Set *tem_ctrl_port* variable to the serial port of the temperature controller.

In *sequence* section, user shall define the sequence of the test procedure. Each entry consists of:
- *cli_cmd*: command to send to hardware. Consistent with standalone usage.
- *time_type*: time to rund the command can be defined as absolute (from the start of the sequence) or relative (a certain time after the last executed command). Use *"abs"* or *"rel"*
- *time* time in seconds (can be a fraction) that specifies when the command shall be executed. Behaviour depends on *time_type*
- *repeat*: specifies how many times a command shall be repeated. Use *0* to execute the command only once.
- *interval*: time in seconds between repeated execution of the command. Set to *0* if repeat functionality is not used for the command.

> Note: last command should always be *"ENDSEQUENCE"*. This lets hardware and data parser know that the sequence is finished.

A basic configuration example is provided in this repository.

#### Test sequence programing notes
- Timing of command execution is handled by hardware. At the start of sequence, commands are loaded into a execution queue on hardware. Transfer of commands takes some time, thus scheduling commands earlier than *10s* into the sequence is not allowed.
- If there are more commands than the length of command queue on hardware (128), additional commands will be loaded during the sequence. Do not schedule a large number of commands with little space (<50ms) between. This might result in missed commands.
- After a command is executed on hardware, data is transfered via the serial interface. In case of buffer dumps, this can take up to several seconds. If the next command is scheduled before the transfer is finished, its execution will be delayed. Check timing requirements in standalone operation. Most functions report their execution time to debug serial (accessible through STLINK debug connector)
- Parsing of incoming data is independent of command scheduling. All commands supported by HW's command line interface can be scheduled and executed, but not all can be parsed and saved. Additional parsing can be implemented by following the instructions in *lsk_py_data_in_parser.py*. Incoming data that does not have a parser implemented will be skipped, but will still be visible in *serial_log.txt*.
- Validity of the commands in *config.py* is **not** checked. It is expected that user inputs only valid and correct commands. Failure to do so might result in undefined behaviour. It is highly recomended to test every command in standalone operation
- In case of issues, reviewing *serial_log.txt* is a good practice.
- If an exception is raised during execution or the keyboard interrupt is triggered (user presses *ctrl+c*), this code will attempt to disable temperature control and reboot the hardware to stop the sequence.

### Temperature control
Temperature control is done by a TEC-1091 module mounted to the main board. To use it with this Python software, it needs to be connected by a sepparate USB cable and the serial port specified in the *config.json* file. If the module is not connected, set temperature target to *"False"*. In this case, DUT temperature reading will be empty.

### Database structure

Data is saved into a SQLite database. It consists of three tables:
- ***measurement***: Top level table. All parsed measurements are saved here. All have a specified timestamp, in microseconds from sequence start. Measurement type is saved in *meas_type* field. Not all columnds are populated for each measurement, depending on measurement type. Columns:
    - *id*: Unique ID for each measurement
    - *ch[x]*: voltage measurement (unit: V)
    - *ch[x]_curr*: current measurement (unit: mA)
    - *DUT_temp*: temperature of DUT as reported by TEC module
    - *ledtemp*: temperature of LED heatsink
    - *meas_type*: measurement type
    - *sample_count*: number of samples taken (used for sample dump measurements)

    If the measurement generates some extra data (such as sample dump or IV characteristic table), this is saved to the following tables. From those, values are referenced back to a specific measurement by *id*.

- ***bufferdump***: If a measurement generates individual sample data, it is saved here. Each sample has a corresponding *timestamp* and a reference to a measurement that generated the sample in *measurement* table (*measurement_id*). Samples are in a chronological order. If more than one measurement generates samples, those are appended. If interested in samples generated by a specific function, filter by *measurement_id*.

- ***characteristic_iv***: If a measurement generates an IV curve, it is saved here and referenced back by *measurement_id*. *timestamp* is always *0*, as the rows are not time-value pairs but current-voltage points in an IV curve.

- ***testinfo***: Various test parameters, conditions and the generated command list. This data is also saved to *info.txt*. text file.