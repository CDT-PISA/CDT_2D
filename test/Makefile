CXX      := c++
CXXFLAGS := -pedantic-errors -Werror -std=gnu++17 -pg -g -O3
LDFLAGS  := -L/usr/lib -lstdc++ -lm
BUILD    := ./build
OBJ_DIR  := $(BUILD)/objects
APP_DIR  := $(BUILD)/apps
TARGET   := test
INCLUDE  := -I../include/
SRC      := 					   \
	$(wildcard ../src/*.cpp)       \
	$(wildcard ./*.cpp)		       \

OBJECTS := $(SRC:%.cpp=$(OBJ_DIR)/%.o)

all: build $(APP_DIR)/$(TARGET)
	@rm -f ./test
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

debug: CXXFLAGS += -DDEBUG -g
debug: all

release: CXXFLAGS += -O2
release: all

#install:
#	@rm ./test
#	@cp $(APP_DIR)/$(TARGET) $(TARGET)
#
#ready: all install

clean:
	-@rm -rvf $(OBJ_DIR)/*
	-@rm -rvf $(APP_DIR)/*

cleanall: clean
	-@rm -rvf $(BUILD)/src/*
                        
