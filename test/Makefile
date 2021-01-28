CXX      := g++
CXXFLAGS := -Werror -std=c++17 # -pedantic-errors 
LDFLAGS  := #-L /home/delia/lib64 -lstdc++ -lm
TARGET   := main
BUILDIR	 := build
INCLUDE  := -I../include/ -I ../src/triangulation/ -I. -I ../src/
SRCDIR   := ../src
SRC      :=  $(wildcard $(SRCDIR)/*.cpp) 

OBJECTS  := $(BUILDIR)/edge.o $(BUILDIR)/gaugeelement.o $(BUILDIR)/label.o $(BUILDIR)/randomgenerator.o $(BUILDIR)/simplex.o $(BUILDIR)/triangle.o $(BUILDIR)/triangulation.o $(BUILDIR)/vertex.o $(BUILDIR)/main.o

$(BUILDIR):
	@mkdir -p $(BUILDIR)

$(BUILDIR)/edge.o: $(SRCDIR)/edge.cpp
	$(CXX) $(CXXFLAGS) $(INCLUDE) -o $@ -c $<

$(BUILDIR)/gaugeelement.o: $(SRCDIR)/gaugeelement.cpp
	$(CXX) $(CXXFLAGS) $(INCLUDE) -o $@ -c $<

$(BUILDIR)/label.o: $(SRCDIR)/label.cpp
	$(CXX) $(CXXFLAGS) $(INCLUDE) -o $@ -c $<

$(BUILDIR)/randomgenerator.o: $(SRCDIR)/randomgenerator.cpp
	$(CXX) $(CXXFLAGS) $(INCLUDE) -o $@ -c $<

$(BUILDIR)/simplex.o: $(SRCDIR)/simplex.cpp
	$(CXX) $(CXXFLAGS) $(INCLUDE) -o $@ -c $<

$(BUILDIR)/triangle.o: $(SRCDIR)/triangle.cpp
	$(CXX) $(CXXFLAGS) $(INCLUDE) -o $@ -c $<

$(BUILDIR)/triangulation.o: $(SRCDIR)/triangulation.cpp $(wildcard $(SRCDIR)/triangulation/*.cpp)
	$(CXX) $(CXXFLAGS) $(INCLUDE) -o $@ -c $<

$(BUILDIR)/vertex.o: $(SRCDIR)/vertex.cpp
	$(CXX) $(CXXFLAGS) $(INCLUDE) -o $@ -c $<

$(BUILDIR)/main.o: main.cpp
	$(CXX) $(CXXFLAGS) $(INCLUDE) -o $@ -c $<

main: $(BUILDIR)/main.o $(OBJECTS)
	$(CXX) $(CXXFLAGS) $(INCLUDE) -o $@ $^	 

all: main

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
                        
