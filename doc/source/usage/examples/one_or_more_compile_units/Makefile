.SUFFIXES:

CC := gcc -c
LD := gcc 

CC_OPTS := -g
LD_OPTS :=

.PHONY: a_test
a_test: a_test.exe
	./a_test.exe

a_test.exe: a_1.c.obj a_2.c.obj a_test.c.obj mockup.c.obj
	$(LD) $(LD_OPTS) $(CC_OPTS) -o $@ $^


-include $(patsubst %.c,%.c.d,$(wildcard *.c))
%.c.obj: %.c
	$(CC) $(CC_OPTS) -MMD -o $@ $<

a.obj: a_1.c.obj a_2.c.obj
	$(LD) $(LD_OPTS) -r -nostdlib -o $@ $^

a_test.c.obj: mockup.c

mockup.c: a.obj
	python -m hammocking --source a_1.c a_2.c --plink a.obj --style plain_c --outdir . $(CC_OPTS)

.PHONY: clean
clean:
	rm -rf a_test.exe *.obj *.d mockup.c mockup.h

