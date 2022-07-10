#ifndef _MOCKUP_H
#define _MOCKUP_H

#define MOCKUP_INCLUDES
#define MOCKUP_DECLARATIONS
#define MOCKUP_ADDITIONAL_GLOBAL_VARIABLES
#include "mockups.mockup"
#undef MOCKUP_INCLUDES
#undef MOCKUP_DECLARATIONS
#undef MOCKUP_ADDITIONAL_GLOBAL_VARIABLES

extern void mockup_hook_init(void);
extern void mockup_hook_pre_test(void);
extern void mockup_hook_post_test(void);
#endif // _MOCKUP_H
