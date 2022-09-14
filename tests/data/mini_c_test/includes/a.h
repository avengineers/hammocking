#ifndef a_h
#define a_h

void a_init(void);
void a_step(void);

extern int a_u1;
extern int a_y1;

void a_set_u2(int u2);
int a_get_y2(void);

void a_set_u3_and_u4(int u3, int u4);
int a_get_y3_and_set_u5(int u5);

typedef int a_y4_t;
extern a_y4_t a_y4;

typedef int a_u6_t;
void a_set_u6(a_u6_t u6);

typedef int a_y5_t;
a_y5_t a_get_y5(void);

void a_get_y6(int *y6);

#endif /* a_h */
