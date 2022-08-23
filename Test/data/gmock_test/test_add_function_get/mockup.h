#ifndef mockup_h
#define mockup_h

#include "gmock/gmock.h" 

extern "C" {
} /* extern "C" */

class class_mockup {

   public:
      MOCK_METHOD((int), a_get_y2, ());
}; /* class_mockup */

extern class_mockup *mockup_global_ptr;

#define CREATE_MOCK(name)   class_mockup name; mockup_global_ptr = &name;

#endif /* mockup_h */
