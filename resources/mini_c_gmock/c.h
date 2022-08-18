#ifndef c_h
#define c_h

void c_init(void);
void c_step(void);

extern int c_u1;
extern int c_y1;

void c_set_u2(int u2);
int c_get_y2(void);

void c_set_u3_and_u4(int u3, int u4);
int c_get_y3_and_set_u5(int u5);

typedef int c_y4_t;
extern c_y4_t c_y4;

typedef int c_u6_t;
void c_set_u6(c_u6_t u6);

typedef int c_y5_t;
c_y5_t c_get_y5(void);

void c_get_y6(int *y6);
#endif /* c_h */
