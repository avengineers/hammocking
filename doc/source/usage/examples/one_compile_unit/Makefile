.SUFFIXES:

CC := gcc -c
LD := gcc 

CC_OPTS := -g
LD_OPTS :=

.PHONY: a_test
a_test: a_test.exe
	./a_test.exe

a_test.exe: a.c.obj a_test.c.obj mockup.c.obj
	$(LD) $(LD_OPTS) $(CC_OPTS) -o $@ $^


-include $(patsubst %.c,%.c.d,$(wildcard *.c))
%.c.obj: %.c
	$(CC) $(CC_OPTS) -MMD -o $@ $<




a_test.c.obj: mockup.c

mockup.c: a.c.obj
	python -m hammocking --source a.c --plink a.c.obj --style plain_c --outdir . $(CC_OPTS)

.PHONY: clean
clean:
	rm -rf a_test.exe *.obj *.d mockup.c mockup.h

