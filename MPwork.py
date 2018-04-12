#########################################################################
# File Name: MPwork.py
# Author: wwang
# mail: 750636248@qq.com
# Created Time: 2018年04月12日 星期四 18时53分44秒
#########################################################################

import numpy as np, sys, math, os
from multiprocessing import Queue
from multiprocessing import Process
from multiprocessing import Manager
import time

class Work:
    def __init__(self, n_jobs = 4):
        self.n_jobs = n_jobs
        self.q_in = Queue(2 * n_jobs) #input queue
        self.q_out = Queue() #output queue
        self.q_slave = Queue(n_jobs) #if full, slave run over
        self.q_d_over = Queue(1) #if full, master run over
        self.master_p = Process(target = self.master)
        self.slaves_p = [Process(target = self.slave) for _ in range(n_jobs)]
        self.run()
        self.result = self.merge()

    def slave(self):
        while not (self.q_d_over.full() and self.q_in.empty()):
            try:
                v = self.q_in.get(True, 1) #find a job
            except Exception as e:
                continue
            for r in self.work(v): #work hard
                self.q_out.put(r)
        self.q_slave.put('ok') #work over

    def master(self):
        for w in self.work_list(): #distribute work
            self.q_in.put(w)
        self.q_d_over.put('over') #distribute over

    def merge(self):
        st = set()
        while not (self.q_slave.full() and self.q_out.empty()):
            try:
                v = self.q_out.get(True, 1) #get a output
            except Exception as e:
                continue
            st.add(v)
        return st

    def run(self):
        self.master_p.start()
        for s in self.slaves_p:
            s.start()

    def join(self):
        self.master_p.join()
        for s in self.slaves_p:
            s.join()

    @staticmethod
    def work(v):
        # you should overwrite this method
        # v is an input from work_list
        # you must return an iterable object or using "yield"
        time.sleep(1)
        yield v
        yield v + 3
        yield v * v

    @staticmethod
    def work_list():
        # you should overwrite this method
        # work_list
        # you must return an iterable object or using "yield"
        return [1,2,3,2,3,1,3,5,3,1,1,2,4,2,4,5,3,1,3,4]

class Work2(Work):
    @staticmethod
    def work(v):
        time.sleep(1)
        for i in range(v):
            yield i
            yield i + 3
            yield i * i

    @staticmethod
    def work_list():
        return range(100)


def main():
    print('hello world, MPwork.py')
    w = Work2(20)
    w.join()
    print(w.result)

if __name__ == '__main__':
    main()

