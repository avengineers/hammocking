#include "mockup.h"

mock_ptr_t mockup_global_ptr = nullptr;



int a_get_y2(){
    if(mockup_global_ptr)
        return mockup_global_ptr->a_get_y2();
    else
        return (int)0;
} /* a_get_y2 */
