#include "mockup.h"

class_mockup *mockup_global_ptr = 0;



int a_get_y2(){
    if(0 != mockup_global_ptr)
        return mockup_global_ptr->a_get_y2();
    else
        return (int)0;
} /* a_get_y2 */
