#ifndef mockup_h
#define mockup_h

#include "gmock/gmock.h" 

extern "C" {
#include "a.h"
#include "c.h"
} /* extern "C" */

class class_mockup {

   public:
      MOCK_METHOD((int), a_get_y2, ());
      MOCK_METHOD((int), a_get_y3_and_set_u5, (int));
      MOCK_METHOD((a_y5_t), a_get_y5, ());
      MOCK_METHOD((void), a_get_y6, (int*));
      MOCK_METHOD((int), c_get_y3_and_set_u5, (int));
      MOCK_METHOD((void), c_set_u2, (int));
      MOCK_METHOD((void), c_set_u3_and_u4, (int, int));
      MOCK_METHOD((void), c_set_u6, (c_u6_t));
}; /* class_mockup */

extern class_mockup *mockup_global_ptr;

#define CREATE_MOCK(name)   class_mockup name; mockup_global_ptr = &name;

#endif /* mockup_h */
