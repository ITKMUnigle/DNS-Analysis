# DNS解析工具
DNSAnalysis,DNS解析，DNS解析小工具----个人学习使用
这是一款支持多平台的DNS解析工具（目前支持 Windows 和 Linux）

## 环境
- JDK1.8

## 注意
- Windows用户：由于hosts文件一般不支持除了administrator的用户的写入 最好以管理员身份运行
- Linux用： Ubuntu请用使用 sudo 或者其他的使用root账户 （目前只有linux版的jar包）

## 使用教程

#### 【1】window安装完成 以管理员身份启动即可

#### 【2】linux需要安装 （目前只测试了Ubuntu18.04）
1. sudo apt-get update -y  //更新软件包
2. sudo apt-get install  -y openjdk-8-jdk  //安装jdk1.8
3. java -version  //查看安装情况 （出现版本号1.8即可）
4. sudo java -jar ResovleDNS.jar //执行程序

## 贡献者
sukeme --饥荒好友


# DNS resolution tool
DNSAnalysis, DNS resolution, DNS resolution small tools-personal learning and use
This is a DNS resolution tool that supports multiple platforms (currently supports Windows and Linux)

## surroundings
- JDK1.8

## Note
- Windows users: As the hosts file generally does not support writing by users other than the administrator, it is best to run as an administrator
- For Linux: For Ubuntu, please use sudo or other root account (currently only the jar package of linux version)

## Tutorial

#### [1] Windows installation is complete, just start it as an administrator

#### [2] linux needs to be installed (currently only tested on Ubuntu 18.04)
1. sudo apt-get update -y //Update software package
2. sudo apt-get install -y openjdk-8-jdk //install jdk1.8
3. java -version //Check the installation situation (version number 1.8 appears)
4. sudo java -jar ResovleDNS.jar //execute the program

## Contributor
sukeme --Famine Friends
