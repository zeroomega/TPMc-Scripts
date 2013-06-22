/*server.c
作者：陈宇杰
功能：接受客户端发来的数据
时间：2013 6/21
*/

#include<stddef.h>
#include<stdio.h>
#include<stdlib.h>
#include<errno.h>
#include<sys/socket.h>
#include<sys/un.h>
#include<unistd.h>

#include</root/jiang/tvd/xensocket/xensocket.h>

#define MAX_LEN 40960

int main()
{
 int sock;
 struct sockaddr_xe server; //声明套接字
long ret;
 char dom_name[255];
 char recvbuf[MAX_LEN];
 char sendbuf[255];
 long i;

 memset(sendbuf,0,255);
 memset(recvbuf,0,MAX_LEN);
 memset(dom_name,0,255);
 printf("请输入本服务器ID：");
 scanf("%s",dom_name);
 server.sxe_family=AF_XEN; //设置网络模式
 server.remote_domid=atoi(dom_name); //获取客户端的id号
 printf("dom_id=%d\n",server.remote_domid);
 //创建套接字
 sock=socket(21,SOCK_STREAM,-1); //注：不知道为什么第一个参数取21，第三个参数取－1
 if(sock<0)
 {
 printf("创建套接字失败！");
 exit(-1);
 }

 ret=bind(sock,(struct sockaddr *)&server,sizeof(server));//绑定套接字
  printf("ret=%d\n",ret); //供调试使用
 
//接收消息
  printf("listening:\n");
 while(1){
         
         ret=recv(sock,recvbuf,MAX_LEN,0);
         if(ret<0)
          {
          printf("接受客户端消息失败！错误号：%d\n",ret);
          break;
        }
    
//输出接收的消息
       recvbuf[ret]='\0';
     if(!strcmp(recvbuf,"quit")) //接收到客户端的中断连接命令
    {
     break;
    }
      else{
     printf("-received-@-:");
     printf("%s\n",recvbuf);  
        }  
     }
 shutdown(sock,SHUT_RDWR); //关闭套接字
return ret;
 }
 
