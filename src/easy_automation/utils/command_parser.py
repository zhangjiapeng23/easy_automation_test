#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: James Zhang
# @data  : 2021/7/19

import argparse

from easy_automation.core.template_command import TemplateCommand


def command_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('startproj',
                        type=str,
                        help='Create a root directory of automation test project ')
    parser.add_argument('project_name',
                        type=str,
                        help='project folder name')
    args = parser.parse_args()
    template_command = TemplateCommand(action=args.startproj, name=args.project_name)
    template_command.handle()


if __name__ == '__main__':
    command_parser()