#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: James Zhang
# @data  : 2024/3/8
import asyncio
import argparse

from easy_automation.service.service_control import start_service


def command_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('port',
                        type=int,
                        help='端口号')
    args = parser.parse_args()
    launch_app(args.port)


def launch_app(port):
    asyncio.run(start_service(port))


if __name__ == '__main__':
    command_parser()
