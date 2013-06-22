/*client.c
 作者：陈宇杰；
 功能：客户端程序，连接服务器，并向其发送消息
 日期：2013 6／21
*/

 #include<stdio.h>
 #include<stdlib.h>
 #include<sys/socket.h>
 #include<sys/un.h>
 #include<unistd.h>
 #include<stddef.h>

#include</root/jiang/tvd/xensocket/xensocket.h>
  
 #define MAX_LEN   40960//发送报文的最大长度
 int main()
 {
  int sock;
  struct sockaddr_xe server;
  long ret;
  long i=0;
  long ret2=0; 
  char sendbuf[MAX_LEN]; //发送缓冲区
  char recvbuf[MAX_LEN]; //接收缓冲区
  char dom_name[255];  //服务器名字字符串
  memset(sendbuf,0,MAX_LEN);
  memset(recvbuf,0,MAX_LEN);
  memset(dom_name,0,255);
  printf("请输入你要连接的服务器名字：%s",dom_name);
  scanf("%s",dom_name);
  server.sxe_family=AF_XEN;
  server.remote_domid=atoi(dom_name);
  server.shared_page_gref=-1;
  printf("连接的虚拟机id = %d\n",server.remote_domid);
   //创建套接字
   sock=socket(21,SOCK_STREAM,-1);//同样不知道21和－1参数原因？
   if(sock<0)
  {
   printf("创建套接字失败！\n");
    exit (-1);
   }
   //连接远程机器
  ret=connect(sock,(struct sockaddr *)&server,sizeof(server));
  if(ret<0)
 {
  printf("连接远程服务器失败！\n");
  exit(-1);
  }

  printf("sending message:\n");
  while(1)
  {
  printf("-input-@-:");
  scanf("%s",sendbuf);
  ret=send(sock,sendbuf,strlen(sendbuf),0);//发送
 if(!strcmp(sendbuf,"quit")){ //中断连接命令
  sleep(2);
  printf("客户端已经退出！\n");  //这个必须，要不然就用sleep代替，否则会由于延迟，使得服务器中某些语句循环
  break;
  }
//接收服务器消息
  /*ret2=recv(sock,recvbuf,sizeof(recvbuf),0);
  if(ret2<=0)
  {
  printf("接收服务器命令失败！\n");
  break;
  }
  recvbuf[ret2]='\0';
  printf("%s",recvbuf);*/
   }
  shutdown(sock,SHUT_RDWR);//关闭套接字
  return ret;
  }
 
