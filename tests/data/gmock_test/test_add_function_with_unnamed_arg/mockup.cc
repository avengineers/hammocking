#include "mockup.h"

class_mockup *mockup_global_ptr = 0;



float my_func(float unnamed1){
    if(0 != mockup_global_ptr)
        return mockup_global_ptr->my_func(unnamed1);
    else
        return (float)0;
} /* my_func */
