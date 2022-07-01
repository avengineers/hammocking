OUTDIR := out
SRC := main.c b.c
OUT := $(OUTDIR)/main

INCLUDES:=$(OUTDIR)

OBJ := $(addprefix $(OUTDIR)/,$(SRC:.c=.o))
ASTS:= $(addprefix $(OUTDIR)/,$(SRC:.c=.ast))

MOCK_SRC := mockup.c
MASTER_MOCK := $(OUTDIR)/mockups.mockup
MOCKUP_CONFIG:=$(OUTDIR)/mockup_config.h
MOCK_OBJ := $(addprefix $(OUTDIR)/,$(MOCK_SRC:.c=.o))

CC := clang
CLANG:=clang

CFLAGS:=$(addprefix -I,$(INCLUDES))

$(OUT): $(OBJ) $(MOCK_OBJ) | $(OUTDIR)
	$(CC) -o $@ $^

$(MOCK_OBJ): $(MOCK_SRC) $(MASTER_MOCK)
$(MOCK_OBJ): CFLAGS += --include $(MOCKUP_CONFIG)
$(MASTER_MOCK): $(ASTS)
	# Here be the magic stuff
	# Loop the list of input files into a response files, for the colleagues using crappy operating systems
	$(file >$@.inputs,$^)
	python3 hammock.py @$@.inputs --symbols c some_var -o $@ --config $(MOCKUP_CONFIG)

$(OUTDIR):
	mkdir -p $@
$(OUTDIR)/%.o: %.c  | $(OUTDIR)
	$(CLANG) -c $< $(CFLAGS) -o $@

$(OUTDIR)/%.ast: %.c
	$(CLANG) -Xclang -ast-dump=json -fsyntax-only  $(CFLAGS) $< > $@

clean:
	rm -rf $(OUTDIR)
