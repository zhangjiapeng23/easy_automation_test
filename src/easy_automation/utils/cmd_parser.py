#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: James Zhang
# @data  : 2021/7/19

import argparse


def cmd_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('create_project',
                        type=str,
                        choices=('startWebProject', 'startApiProject', 'startMobileProject'),
                        help='select a kind of project to create: web_template, api_template, mobile_template')
    parser.add_argument('project_name',
                        type=str,
                        help='project folder name')
    args = parser.parse_args()
    print(args.create_project, args.project_name)


if __name__ == '__main__':
    cmd_parser()
