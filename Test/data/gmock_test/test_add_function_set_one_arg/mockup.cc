#include "mockup.h"

class_mockup *mockup_global_ptr = 0;



void set_some_int(int some_value){
    if(0 != mockup_global_ptr)
        mockup_global_ptr->set_some_int(some_value);
} /* set_some_int */
