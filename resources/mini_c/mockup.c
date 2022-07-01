#include "mockup.h"

#define extern
#define MOCKUP_ADDITIONAL_GLOBAL_VARIABLES
#include "mockups.mockup"
#undef MOCKUP_ADDITIONAL_GLOBAL_VARIABLES
#undef extern

#define MOCKUP_CODE
#include "mockups.mockup"
#undef MOCKUP_CODE

void mockup_hook_init(void) 
{
#define MOCKUP_HOOK_INIT_CALL
#include "mockups.mockup"
#undef MOCKUP_HOOK_INIT_CALL
}

void mockup_hook_pre_test(void)
{
#define MOCKUP_HOOK_TEST_START
#include "mockups.mockup"
#undef MOCKUP_HOOK_TEST_START
}
void mockup_hook_post_test(void)
{
#define MOCKUP_HOOK_TEST_END
#include "mockups.mockup"
#undef MOCKUP_HOOK_TEST_END
}
