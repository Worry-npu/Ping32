# 数据安全共享系统初版：

```
本项目是一个简化的文件管理与审计平台，基于 **Flask + SQLite** 实现，支持用户身份验证、文件加密上传与下载、文件删除、日志审计等功能。
```

## 1.项目结构说明
![image](https://github.com/user-attachments/assets/5c4db38b-6bb7-4a8b-9264-1490d28d0ca2)


## 2. 运行项目

#### 2.1在终端运行该命令，成功下载所用环境

```
pip install -r requirements.txt
```

#### 2.2运行主文件

```bash
python app.py
```

浏览器访问 [http://localhost:5000](http://localhost:5000/) 即可。

------



## 3.运行示例

#### 步骤1：点击app.py运行

![image-20250527122715625](C:\Users\ASUS\AppData\Roaming\Typora\typora-user-images\image-20250527122715625.png)

#### 步骤2：点击 `* Running on http://127.0.0.1:5000`

#### 步骤3：利用初始密码登录

![image-20250527122812559](C:\Users\ASUS\AppData\Roaming\Typora\typora-user-images\image-20250527122812559.png)

#### 步骤4：可以进行上传，下载，删除文档

![image-20250527122900492](C:\Users\ASUS\AppData\Roaming\Typora\typora-user-images\image-20250527122900492.png)

#### 步骤5：点击操作日志，可以查看日志内容

![image-20250527122930191](C:\Users\ASUS\AppData\Roaming\Typora\typora-user-images\image-20250527122930191.png)
