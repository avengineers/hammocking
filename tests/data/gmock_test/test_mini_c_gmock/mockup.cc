#include "mockup.h"

class_mockup *mockup_global_ptr = 0;

int a_y1;
a_y4_t a_y4;
int c_u1;


int a_get_y2(){
    if(0 != mockup_global_ptr)
        return mockup_global_ptr->a_get_y2();
    else
        return (int)0;
} /* a_get_y2 */

int a_get_y3_and_set_u5(int u5){
    if(0 != mockup_global_ptr)
        return mockup_global_ptr->a_get_y3_and_set_u5(u5);
    else
        return (int)0;
} /* a_get_y3_and_set_u5 */

a_y5_t a_get_y5(){
    if(0 != mockup_global_ptr)
        return mockup_global_ptr->a_get_y5();
    else
        return (a_y5_t)0;
} /* a_get_y5 */

void a_get_y6(int* y6){
    if(0 != mockup_global_ptr)
        mockup_global_ptr->a_get_y6(y6);
} /* a_get_y6 */

int c_get_y3_and_set_u5(int u5){
    if(0 != mockup_global_ptr)
        return mockup_global_ptr->c_get_y3_and_set_u5(u5);
    else
        return (int)0;
} /* c_get_y3_and_set_u5 */

void c_set_u2(int u2){
    if(0 != mockup_global_ptr)
        mockup_global_ptr->c_set_u2(u2);
} /* c_set_u2 */

void c_set_u3_and_u4(int u3, int u4){
    if(0 != mockup_global_ptr)
        mockup_global_ptr->c_set_u3_and_u4(u3, u4);
} /* c_set_u3_and_u4 */

void c_set_u6(c_u6_t u6){
    if(0 != mockup_global_ptr)
        mockup_global_ptr->c_set_u6(u6);
} /* c_set_u6 */
