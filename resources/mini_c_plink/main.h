#ifndef MAIN_H
#define MAIN_H

extern int some_var;

extern int b(void);
extern int c(void);

#ifdef CFG_D
extern int d(int n);
#endif /* CFG_D */

#endif
