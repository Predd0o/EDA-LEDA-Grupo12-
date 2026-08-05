#!/bin/sh
set -e
cd "$(dirname "$0")"
javac -d . Main.java segmentTree.java
