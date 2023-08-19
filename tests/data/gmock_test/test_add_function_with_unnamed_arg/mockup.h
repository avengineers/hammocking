#ifndef mockup_h
#define mockup_h

#include "gmock/gmock.h" 

extern "C" {
} /* extern "C" */

class class_mockup;
typedef class_mockup* mock_ptr_t;
extern mock_ptr_t mockup_global_ptr;

class class_mockup {

 public:
   class_mockup()  { mockup_global_ptr = this; }
   ~class_mockup() { mockup_global_ptr = nullptr; }
   MOCK_METHOD((float), my_func, (float));
}; /* class_mockup */

/* Version A: Create a local object that is destroyed when out of scope */
#define LOCAL_MOCK(name)   class_mockup name

/* Version B: Allocate an object that will be only explicitly deallocated */
#define CREATE_MOCK()     new class_mockup                                                                                                       
#define DESTROY_MOCK()    {if(mockup_global_ptr) delete mockup_global_ptr;}

#endif /* mockup_h */
