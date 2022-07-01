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

define newline


endef

CC := clang
CLANG:=clang

CFLAGS:=$(addprefix -I,$(INCLUDES))

$(OUT): $(OBJ) $(MOCK_OBJ) | $(OUTDIR)
	$(CC) -o $@ $^

$(MOCK_OBJ): $(MOCK_SRC) $(MASTER_MOCK)
$(MOCK_OBJ): EXTRA_INCLUDE := --include $(MOCKUP_CONFIG)
$(MASTER_MOCK) $(MOCKUP_CONFIG) &: $(ASTS)
	# Here be the magic stuff
	# Loop the list of input files into a response files, for the colleagues using crappy operating systems
	$(file >$@.inputs,$(foreach input,$^,$(input)$(newline)))
	python3 hammock.py @$@.inputs --symbols c some_var -o $(MASTER_MOCK) --config $(MOCKUP_CONFIG)

$(OUTDIR):
	mkdir -p $@
$(OUTDIR)/%.o: %.c  | $(OUTDIR)
	$(CLANG) -c $< $(CFLAGS) $(EXTRA_INCLUDE) -o $@

$(OUTDIR)/%.ast: %.c
	$(CLANG) -Xclang -ast-dump=json -fsyntax-only  $(CFLAGS) $< > $@

clean:
	rm -rf $(OUTDIR)
