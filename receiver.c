#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>
#include <errno.h>
#include <sys/socket.h>
#include <sys/un.h>
#include <unistd.h>
#include "../xensocket.h"
#define MAX_MSG_LEN 2048
int main (int argc, char **argv) {
  int sock;
	struct sockaddr_xe sxeaddr;
	int rc = 0;
	int gref;
	unsigned char rcv_buf[MAX_MSG_LEN];
//参数输入domid	    
	if (argc != 2)
	{
		printf("input a domid!\n");
		return -1;
	}

	sxeaddr.sxe_family = AF_XEN;
	sxeaddr.remote_domid = atoi(argv[1]);
	printf("domid = %d\n", sxeaddr.remote_domid);

  /* Create the socket. */
	sock = socket (21, SOCK_STREAM, -1);
	if (sock < 0)
	{
		printf("socket error!\n");
		return -1;
	}
	gref = bind (sock, (struct sockaddr *)&sxeaddr, sizeof(sxeaddr));
	printf("gref = %d\n", gref);
//等待接收
	rc = recv(sock, rcv_buf, MAX_MSG_LEN, 0);
	if (rc < 0 )
		{
	     	printf("recv error!\n");
			perror ("recv");
			return -1;
	   	}
   	printf("%s", rcv_buf);
	putchar('\n');
	shutdown(sock, SHUT_RDWR);
	return 0;
}


