OUT := main
SRC := main.c b.c
OBJ := $(SRC:.c=.o)

CC := clang

$(OUT): $(OBJ)
	$(CC) -o $@ $^

clean:
	rm -rf $(OBJ) $(OUT)
