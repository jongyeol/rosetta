#!/bin/bash
echo Generate Rosetta...
python rosetta/create.py jni gen

echo Build...
ndk-build

