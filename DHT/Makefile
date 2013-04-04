CC = gcc
CFLAGS =  -fPIC -Wall -O2 -std=c99 -I. -lbcm2835
DEPS = 
OBJ = libdht.o

%.o: %.c $(DEPS)
	$(CC) -c -o $@ $< $(CFLAGS)

libdht.so: $(OBJ)
	$(CC) -shared -o $@ $^

.PHONY: clean
clean:
	rm -f $(ALLOBJ) libfli.o libfli.a
