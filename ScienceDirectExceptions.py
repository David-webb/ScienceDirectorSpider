#!/usr/bin/env python
# -*- coding:utf-8 -*-
__author__ = 'Tengwei'

class ParseArticleInfoError(Exception):
    def __init__(self, code):
        elementlist = [
            'show_more_buttom',
            'title',
            'author',
            'author_affliation',
            'dates',
            'dio'
        ]
        self.Message = "No right " + elementlist[(code-1) % 6] +" parsing rule, please update ruleslist manually..."
        # if code == 1:       # 解析show_more按钮的异常
        #     self.Message = "No right show_more_buttom parsing rule, please update ruleslist manually..."
        # elif code == 2:     # 解析文章标题的异常
        #     self.Message = "No right title parsing rule, please update ruleslist manually..."
        # elif code == 3:
        #     self.Message = "No right author parsing rule, please update ruleslist manually..."
        # elif code == 4:
        #     self.Message = "No right author_affliation parsing rule, please update ruleslist manually..."
        # elif code == 5:
        #     self.Message = "No right dates parsing rule, please update ruleslist manually..."
        # elif code == 6:
        #     self.Message = "No right dio parsing rule, please update ruleslist manually..."
        pass
