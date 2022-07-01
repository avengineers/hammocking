OUTDIR := out
SRC := main.c b.c
OUT := $(OUTDIR)/main

INCLUDES:=$(OUTDIR)

OBJ := $(addprefix $(OUTDIR)/,$(SRC:.c=.o))
ASTS:= $(addprefix $(OUTDIR)/,$(SRC:.c=.ast))

MOCK_SRC := mockup.c
MASTER_MOCK := $(OUTDIR)/mockups.mockup
MOCK_OBJ := $(addprefix $(OUTDIR)/,$(MOCK_SRC:.c=.o))

CC := clang
CLANG:=clang

CFLAGS:=$(addprefix -I,$(INCLUDES))

$(OUT): $(OBJ) $(MOCK_OBJ) | $(OUTDIR)
	$(CC) -o $@ $^

$(MOCK_OBJ): $(MOCK_SRC) $(MASTER_MOCK)
$(MASTER_MOCK): $(ASTS)
	# Here be the magic stuff
	python3 hammock.py $^ --symbols c -o $@

$(OUTDIR):
	mkdir -p $@
$(OUTDIR)/%.o: %.c  | $(OUTDIR)
	$(CLANG) -c $< $(CFLAGS) -o $@

$(OUTDIR)/%.ast: %.c
	$(CLANG) -Xclang -ast-dump=json -fsyntax-only  $(CFLAGS) $< > $@

clean:
	rm -rf $(OUTDIR)
