#!/bin/sh

base=$(cd "$(dirname "$0")"; pwd)
cd $base

nohup python weixinspider.py &
