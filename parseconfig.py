import json

with open('config.json') as f:
    config = json.load(f)

cmdlist = []
last_sched_time = 0

for elem in config['sequence']:
    if 'repeat' in elem and elem['repeat'] > 0:
        for i in range(elem['repeat']):
            if elem['time_type'] == 'abs':
                sched_time = elem['time'] * 1000000
            elif elem['time_type'] == 'rel':
                sched_time = last_sched_time + elem['time'] * 1000000
            else:
                raise Exception('time_type Error')
            sched_time += i * elem['interval'] * 1000000
            cmd = f"{elem['cli_cmd']} -sched {sched_time}"
            cmd += "\n"
            cmdlist.append(cmd)
            # print(cmd)
        last_sched_time = sched_time
    else:
        if elem['time_type'] == 'abs':
            sched_time = elem['time'] * 1000000
        elif elem['time_type'] == 'rel':
            sched_time = last_sched_time + elem['time'] * 1000000
        else:
            raise Exception('time_type Error')
        last_sched_time = sched_time
        cmd = f"{elem['cli_cmd']} -sched {sched_time}"
        cmd += "\n"
        cmdlist.append(cmd)
        # print(cmd)

# print cmdlist to console one elemet per line
for cmd in cmdlist:
    print(cmd, end='')
