CXX      := g++
CXXFLAGS := -Werror -std=c++17 # -pedantic-errors 
LDFLAGS  := #-L /home/delia/lib64 -lstdc++ -lm
BUILD    := ./build
OBJ_DIR  := $(BUILD)/objects
APP_DIR  := $(BUILD)/apps
TARGET   := main
INCLUDE  := -I../include/ -I.
SRC      := 					   \
	$(wildcard ../src/*.cpp)       \
	$(wildcard ./*.cpp)		       \

OBJECTS := $(SRC:%.cpp=$(OBJ_DIR)/%.o)

all: build $(APP_DIR)/$(TARGET)
	@rm -f ./main
	@cp $(APP_DIR)/$(TARGET) $(TARGET)	

$(OBJ_DIR)/%.o: %.cpp
	@mkdir -p $(@D)
	$(CXX) $(CXXFLAGS) $(INCLUDE) -o $@ -c $<

$(APP_DIR)/$(TARGET): $(OBJECTS)
	@mkdir -p $(@D)
	$(CXX) $(CXXFLAGS) $(INCLUDE) $(LDFLAGS) -o $(APP_DIR)/$(TARGET) $(OBJECTS)

.PHONY: all build clean debug install ready release

build:
	@mkdir -p $(APP_DIR)
	@mkdir -p $(OBJ_DIR)

debug: CXXFLAGS += -DDEBUG -g -pg
debug: all

release: CXXFLAGS += -O3
release: all

release_U1: CXXFLAGS = -std=c++17 -O3 -DNC=1
release_U1: all

release_SU2: CXXFLAGS = -std=c++17 -O3 -DNC=2
release_SU2: all

#install:
#	@rm ./main
#	@cp $(APP_DIR)/$(TARGET) $(TARGET)
#
#ready: all install

clean:
	-@rm -rvf $(OBJ_DIR)/*
	-@rm -rvf $(APP_DIR)/*

cleanall: clean
	-@rm -rvf $(BUILD)/src/*
                        
