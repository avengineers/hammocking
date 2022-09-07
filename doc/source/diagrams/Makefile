
infiles = $(wildcard *.uxf)
outfiles_svg = $(patsubst %.uxf,%.uxf.svg,$(infiles))
outfiles_png = $(patsubst %.uxf,%.uxf.png,$(infiles))

$(info $(outfiles_svg))

ifeq ($(OS),Windows_NT)
    UMLET=Umlet_cmd
else
	UMLET=umlet
endif

.PHONY: all
all: $(outfiles_svg) $(outfiles_png)

%.uxf.svg: %.uxf
	$(UMLET) -action=convert -format=svg -filename=$< -output=$@

%.uxf.png: %.uxf
	$(UMLET) -action=convert -format=png -filename=$< -output=$@
 
.PHONY: clean
clean:
	rm -rf $(outfiles_svg) $(outfiles_png)
	