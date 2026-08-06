CXX      ?= g++
CXXFLAGS ?= -std=c++17 -O2 -Wall -Iinclude

SRC    := src/main.cpp src/SegmentTree.cpp
TARGET := build/segtree_cpp

all: $(TARGET)

$(TARGET): $(SRC) include/SegmentTree.h
	mkdir -p build
	$(CXX) $(CXXFLAGS) $(SRC) -o $(TARGET)

clean:
	rm -rf build

.PHONY: all clean
