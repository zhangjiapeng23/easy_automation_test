#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: James Zhang
# @data  : 2021/7/21
import argparse

from easy_automation.core.template_command import TemplateCommand

def manage():
    parser = argparse.ArgumentParser()
    parser.add_argument('startapp',
                        type=str,
                        choices=['startwebapp', 'startapiapp'],
                        help='Create an app of web or api automation test')
    parser.add_argument('app_name',
                        type=str,
                        help='App name')
    args = parser.parse_args()
    template_command = TemplateCommand(action=args.startapp, name=args.app_name)
    template_command.handle()


if __name__ == '__main__':
    manage()