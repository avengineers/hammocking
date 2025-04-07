#include "a.h"
#include "b.h"
#include "c.h"

void a_some_func(void){
    int x = b_getX();
    int y = x;
    c_setY(y);
}
