CC = gcc
CFLAGS =  -fPIC -Wall -O2 -std=c99 
LIBS = -lwiringPi
ALLOBJ = libdht.o

%.o: %.c
	$(CC) -c -o $@ $< $(CFLAGS)

libdht.so: $(ALLOBJ)
	$(CC) -shared -o $@ $^ $(LIBS)

.PHONY: clean
clean:
	rm -f $$(find . | grep "[.]pyc")
	rm -f $$(find . | grep "~$$")
	rm -f $(ALLOBJ) libdht.so
