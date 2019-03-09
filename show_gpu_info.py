#########################################################################
# File Name: gpu.py
# Author: wwang
# mail: 750636248@qq.com
# Created Time: 2018年01月09日 星期二 19时24分27秒
#########################################################################

import numpy as np, sys, math, os
import re
import time

def color_str(s, i):
    return '\033[1;3{};40m{}\033[0m'.format(i + 2, s)

class ShowGpuInfo:
    def __init__(self):
        self.run()
        
    def get_gpu_info(self):
        f = os.popen('nvidia-smi')
        self.lines = []
        for s in f:
            self.lines.append(s[:-1])
        f.close()

    def get_cpu_info(self):
        f = os.popen('ps au')
        pid2cpu_info = {}
        for s in f:
            s = s.split()
            if len(s) > 1:
                pid = s[1]
                # user, cpu, mem, time
                info = [s[i] for i in [0, 2, 3, 9]]
                pid2cpu_info[pid] = info
        f.close()
        return pid2cpu_info
    """
    def put_mm(self):
        p = '(\d+)MiB .* (\d+)MiB .* (\d+)%'
        for i, l in enumerate(self.lines):
            r = re.findall(p, l)
            if i and r:
                v = int(r[0][-1])
                a, b = int(r[0][0]), int(r[0][1])
                s = '剩余{:4.1f}G {:3.0f}%'.format((b - a) / 1024, (b - a) / b * 100)
                pl = self.lines[i - 1]
                self.lines[i - 1] = '{}{}{}'.format(pl[:-7 - len(s) - 2], s, pl[-7:])
                s = '{:3.0f}% {:3.0f}%'.format(hm, h[-1])
                pl = self.lines[i]
                self.lines[i] = '{}{}{}'.format(pl[:-13 - len(s)], s, pl[-13:])
    """
    def put_cpu_info(self, pid2cpu_info):
        p = '(\d)\s+(\d+)\s+(\S+)\s+(\S+)\s+(\d+)MiB'
        line_width = None
        header = None
        header_id = None
        table_ids = []
        table = []
        for i, l in enumerate(self.lines):
            if re.match('.*'.join(['', 'Processes:', 'GPU Memory']), l) is not None:
                self.lines[i] = None
                continue
            if re.match('.*'.join(['', 'GPU', 'PID', 'Type', 'Process name']), l) is not None:
                header = ['User', 'GPU', 'PID', 'CMD', 'GPU_Mem', '%cpu', '%mem', 'time']
                header_id = i
                self.lines[i] = None
                line_width = len(l)
                continue
            r = re.findall(p, l)
            if r:
                self.lines[i] = None
                pid = r[0][1]
                cpu_header = ['User', '%cpu', '%mem', 'time']
                cpu_info = pid2cpu_info.get(pid, ['none'] * len(cpu_header))
                info = dict(zip(cpu_header, cpu_info))

                gpu_info = l.split()
                gpu_header = ['GPU', 'PID', 'CMD', 'GPU_Mem']
                gpu_info = [gpu_info[i] for i in [1, 2, 4, 5]]
                info.update(dict(zip(gpu_header, gpu_info)))
                info = [info[h] for h in header]
                table.append(info)
                table_ids.append(i)
        col_max = [0] * len(header)
        for line in [header] + table:
            for i, l in enumerate(line):
                col_max[i] = max(col_max[i], len(l))
        def get_line(line):
            gpu = line[1]
            ws = []
            for max_width, word in zip(col_max, line):
                #ws.append('{}{}'.format(word, ' ' * (max_width - len(word))))
                ws.append('{}{}'.format(' ' * (max_width - len(word)), word))
            s = '  '.join(ws)
            space = line_width - len(s) - 2
            left = space // 2
            right = space - left
            if len(gpu) == 1:
                s = color_str(s, int(gpu))
            s = '|{}{}{}|'.format(' ' * left, s, ' ' * right)
            return s

            
        self.lines[header_id] = get_line(header)
        for i, t in zip(table_ids, table):
            self.lines[i] = get_line(t)

    def show(self):
        for l in self.lines:
            if l is not None:
                print(l)
        line = ' ' * 79
        print(line)
        #print(self.lines[-1], end = '', flush = True)

    def run(self):
        os.system('clear')
        while True:
            self.get_gpu_info()
            #self.put_vu()
            pid2cpu_info = self.get_cpu_info()
            self.put_cpu_info(pid2cpu_info)
            self.show()
            os.system('tput cup 0 0')
            time.sleep(1)
            #return

def main():
    print('hello world, gpu.py')
    s = ShowGpuInfo()
    #s.update_pid2user()
    #print(s.pid2user)

if __name__ == '__main__':
    main()

