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
    def __init__(self, nb_gpus = 4):
        self.nb_gpus = nb_gpus
        self.history = [[] for i in range(self.nb_gpus)]
        self.nb_history = 10
        self.avn = 20
        self.a = []

        self.run()
        
    def get_gpu_info(self):
        f = os.popen('nvidia-smi')
        self.lines = []
        for s in f:
            self.lines.append(s[:-1])
        f.close()

    def put_vu(self):
        p = '(\d+)MiB .* (\d+)MiB .* (\d+)%'
        gid = 0
        for i, l in enumerate(self.lines):
            r = re.findall(p, l)
            if i and r:
                v = int(r[0][-1])
                self.history[gid].append(v)
                a, b = int(r[0][0]), int(r[0][1])
                s = '剩余 {:4.1f}G {:3.0f}%'.format((b - a) / 1024, (b - a) / b * 100)
                pl = self.lines[i - 1]
                self.lines[i - 1] = '{}{}{}'.format(pl[:-7 - len(s) - 2], s, pl[-7:])
                h = self.history[gid]
                hm = np.mean(h[-self.nb_history:])
                if hm < self.avn and h[-1] < self.avn: self.a.append(str(gid))
                s = '{:3.0f}% {:3.0f}%'.format(hm, h[-1])
                pl = self.lines[i]
                self.lines[i] = '{}{}{}'.format(pl[:-13 - len(s)], s, pl[-13:])
                gid += 1
        if len(self.history[0]) > 3600:
            for i in range(self.nb_gpus):
                self.history[i] = self.history[i][-self.nb_history:]

    def put_un(self):
        p = '(\d)\s+(\d+)\s+(\S+)\s+(\S+)\s+(\d+)MiB'
        gid = 0
        for i, l in enumerate(self.lines):
            r = re.findall(p, l)
            if i and r:
                v = r[0][1]
                s = '{} {}'.format(r[0][0], self.pid2user[v])
                l = self.lines[i]
                self.lines[i] = '{}{}{}'.format(l[:-22], s, l[-22 + len(s):])
                self.lines[i] = color_str(self.lines[i], int(r[0][0]))
                if int(r[0][-1]) < 100:
                    self.lines[i] = None
                gid += 1

    def show(self):
        for l in self.lines:
            if l is not None:
                print(l)
        if self.a:
            print('可用：{}'.format(','.join(self.a)))
        else:
            print('满了!')
        print(' ' * 80)
        #print(self.lines[-1], end = '', flush = True)

    def run(self):
        os.system('clear')
        while True:
            self.a = []
            self.get_gpu_info()
            self.put_vu()
            self.update_pid2user()
            self.put_un()
            self.show()
            os.system('tput cup 0 0')
            time.sleep(1)
            #return

    def update_pid2user(self):
        f = os.popen('ps au')
        pids, users = [], []
        for i, s in enumerate(f):
            s = s.split()
            if len(s) > 1:
                users.append(s[0])
                pids.append(s[1])
        f.close()
        self.pid2user = dict(zip(pids, users))

def main():
    print('hello world, gpu.py')
    s = ShowGpuInfo()
    #s.update_pid2user()
    #print(s.pid2user)

if __name__ == '__main__':
    main()

