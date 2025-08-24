#!/bin/bash

echo "=== Raspberry Pi Environment Check ==="
echo "Node.js version:"
node --version
echo "npm version:"
npm --version
echo "Architecture:"
uname -m
echo "OS:"
cat /etc/os-release | grep PRETTY_NAME
echo "Memory:"
free -h
echo "CPU:"
cat /proc/cpuinfo | grep "Model name" | head -1
