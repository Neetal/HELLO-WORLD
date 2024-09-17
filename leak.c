#include <stdio.h>
#include <stdlib.h>
#include <string.h>
 
#define KB1     1024
#define MEMSIZE (4 * KB1)
 
char *string = "IDENTIFY 10 ISSUES IN THIS MEMLEAK PROGRAM";
char *gstring = "IDENTIFY 10 ISSUES IN THIS MEMLEAK PROGRAM";
char *gptr;
char *rptr;
int num;
 
char * f1_alloc(void);
char * f2_copyme(void);
void   f3_free(char *, char *);
 
main()
{
    srand((int)getpid());
  //while (getpid() != 0) {
        gptr = f1_alloc();

        memset(gptr,'\0',MEMSIZE);

        strcpy(gptr, string);

        rptr = f2_copyme();
     //   free(gptr);
       // free(rptr);

        f3_free(gptr,rptr);
  // }
}
 
char *f1_alloc()
{
    return (malloc(MEMSIZE));
}
char *f2_copyme()
{
    static int len, i = 0;
    char *s;
    int r;
    len = strlen(string);
    s = (char *)malloc(len);
    memset(s,'\0',len);
    strncpy(s, string, len);
    i++;
    if (!(i % MEMSIZE))
       
        printf("i=%d, %s\n", i, s);

return s;
}
 
void f3_free(char *p,char *q)
{
    num = rand() % 3;
if (!num)
        free(p);
        free(q);
}


