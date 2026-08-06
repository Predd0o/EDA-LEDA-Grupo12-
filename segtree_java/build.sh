#!/bin/sh
set -e
cd "$(dirname "$0")"
javac -encoding UTF-8 -d . Main.java segmentTree.java
