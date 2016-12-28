#!/usr/bin/env python
# -*- coding:utf-8 -*-
__author__ = 'Tengwei'
import threading

def fun_timer():
    print "Hellow Timer!"
    # timer = threading.Timer(5, fun_timer())

for i in range(3):
    count = 1
    timer = threading.Timer(3, fun_timer())
    timer.start()
    timer.cancel()


# **************验证了当没有变量指向对象内存时,类对象的生命周期会停止*******************
#
# class Person:
#     population = 0
#     def __init__(self,name):
#         self.name = name
#         print("initializing %s"%self.name)
#         Person.population += 1
#     def __del__(self):
#         print("%s say bye"%self.name)
#         Person.population -=1
#         if Person.population == 0 :
#             print ("I'm the last one")
#         else:
#             print ("There are still %d person left"%Person.population)
#     def SayHi(self):
#         print ("Hi,my name is %s"%self.name)
#     def HowMany(self):
#         if Person.population == 1:
#             print("I am the only Person here")
#         else:
#             print ("We have %d person here"%Person.population)
#
# for i in range(10):
#     swaroop = Person("Swaroop" + str(i)) #initializing Swaroop
#     swaroop.SayHi()     #Hi,my name is Swaroop



