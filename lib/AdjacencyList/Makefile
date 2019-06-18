CXX      := c++
CXXFLAGS := -pedantic-errors -Werror -std=gnu++17
LDFLAGS  := -L /usr/lib -lstdc++ -lm -lboost_system -lboost_filesystem
BUILD    := ./build
OBJ_DIR  := $(BUILD)/objects
APP_DIR  := $(BUILD)/apps
TARGET   := make_adjacency
INCLUDE  := -I ../../include/
SRC      := $(wildcard ../../src/*.cpp)


OBJ_TMP := $(SRC:%.cpp=$(OBJ_DIR)/%.o)
OBJECTS := $(subst ../,,$(OBJ_TMP))
OBJDIRS := $(shell echo $(OBJECTS) | sed -r "s-[^/]*\.o--g")


all: build $(APP_DIR)/$(TARGET)
	@rm -f ./$(TARGET)
	@cp $(APP_DIR)/$(TARGET) $(TARGET)

$(OBJ_DIR)/%.o: ../../%.cpp
	@echo "building:   $@"
	@$(CXX) $(CXXFLAGS) $(INCLUDE) -o $@ -c $<
#$(eval OBJS := $(shell echo $@ | sed -r "s-^ *$(OBJ_DIR)/(\.\./)*--g"))
#echo $(OBJS)

#.SECONDEXPANSION:
#$(subst ../,,$(OBJ_DIR)/%.o): %.cpp

$(OBJ_DIR)/$(TARGET).o: $(TARGET).cpp
	@echo "building:   $(subst ./,,$(OBJ_DIR))/$(TARGET).o"
	@$(CXX) $(CXXFLAGS) $(INCLUDE) -o $(OBJ_DIR)/$(TARGET).o -c $(TARGET).cpp

$(APP_DIR)/$(TARGET): $(OBJECTS) $(OBJ_DIR)/$(TARGET).o
	@mkdir -p $(@D)
	@echo
	@echo "✾ generating \e[3m $(TARGET) \e[0m binary:"
	@echo "└────────────"
	$(CXX) $(CXXFLAGS) $(INCLUDE) $(LDFLAGS) -o $(APP_DIR)/$(TARGET) $(OBJ_DIR)/$(TARGET).o $(OBJECTS)

	
.PHONY: all build clean debug install read release
	
build:
	@mkdir -p $(APP_DIR)
	@mkdir -p $(OBJ_DIR)
	@mkdir -p $(OBJDIRS)

debug: CXXFLAGS += -DDEBUG -pg -g
debug: all

release: CXXFLAGS += -O3
release: all

#install:
#	@rm ./test
#	@cp $(APP_DIR)/$(TARGET) $(TARGET)
#
#ready: all install

clean:
	-@rm -rvf $(APP_DIR)/*

cleanall: clean
	-@rm -rvf $(OBJ_DIR)/*

read: 
	$(CXX) $(CXXFLAGS) $(INCLUDE) $(LDFLAGS) -o read_adjacency read_adjacency.cpp
