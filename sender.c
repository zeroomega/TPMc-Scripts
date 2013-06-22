#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/socket.h>
#include <sys/un.h>
#include <unistd.h>
#include "../xensocket.h"
#define MAX_MSG_LEN  2048  
int
main (int argc, char **argv) 
{
  int             sock;
  struct          sockaddr_xe sxeaddr;
  int             rc = 0;
  unsigned char send_buf[MAX_MSG_LEN];
  int send_len = 0;
  if (argc !=2) {
    printf("input a domid!");
    return -1;
  }

  sxeaddr.sxe_family = AF_XEN;
  sxeaddr.remote_domid = atoi(argv[1]);
  printf("domid = %d\n", sxeaddr.remote_domid);
  sxeaddr.shared_page_gref = -1;//atoi(argv[2]);

  /* Create the socket. */
  sock = socket (21, SOCK_STREAM, -1);
  if (sock < 0) {
  printf("socket error!\n");
	return -1;
  }

  rc = connect (sock, (struct sockaddr *)&sxeaddr, sizeof(sxeaddr));
  if (rc < 0) {
    printf ("connect failed\n");
    return -1;
  }
  fflush(stdout); 
	printf("Sending...\n");
	send_len = 256;
	memset( send_buf, 0, send_len );
	int i;
	for(i=0;i<send_len;i++)
	{
		if('\n'==(send_buf[i]=getchar()))
			break;
	}
	send_buf[i]=0;
	rc = send(sock, send_buf, i, 0);
  shutdown(sock, SHUT_RDWR);
  return 0;
}
