.SUFFIXES:


.PHONY: a_test
a_test: a_test.exe
	./a_test.exe

a_test.exe: a.c.obj a_test.c.obj mockup.c.obj
	gcc -g -o $@ $^


-include $(patsubst %.c,%.c.d,$(wildcard *.c))
%.c.obj: %.c
	gcc -c -g -MMD -o $@ $<




a_test.c.obj: mockup.c

mockup.c: a.c.obj
	python -m hammock --source a.c --plink a.c.obj --style plain_c --outdir . 

.PHONY: clean
clean:
	rm -rf a_test.exe *.obj *.d mockup.c mockup.h

