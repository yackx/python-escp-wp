samples/$(TARGET).escp.bin: samples/$(TARGET).escp.txt
	source venv/bin/activate && python -m wp.convert $< -o $@ --pins 9

samples: samples/$(TARGET).escp.bin

TXT_FILES := $(wildcard samples/**/*.escp.txt)
BIN_FILES := $(patsubst %.txt, %.bin, $(TXT_FILES))

%.bin: %.txt
	cd $(CURDIR) && source venv/bin/activate && python -m wp.scripts $< -o $@ --pins 9

all_samples: $(BIN_FILES)
