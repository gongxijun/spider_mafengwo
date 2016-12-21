#!/usr/bin/env python
# -*-coding:utf-8-*-
import inspect
import codecs



class Im:
    def __init__(self, int_var):
        self.int_var = [int_var]

        pass

    def func(self, int_var):
        self.int_var.append(int_var + 1)
        print self.int_var
        if len(self.int_var) > 30:
            return
        else:
            self.func(int_var + 1)


for status_ma in codecs.open('city_info', 'r', encoding='utf-8'):
    print status_ma.split('\t')[-1]
