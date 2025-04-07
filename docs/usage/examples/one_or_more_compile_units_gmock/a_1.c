#include "a.h"
#include "b.h"
#include "c.h"

int x;

void a_some_func_1(void){
    x = b_getX();
    int y = x;
    c_setY(y);
}
