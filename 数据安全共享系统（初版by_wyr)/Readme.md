# 数据安全共享系统初版：

```
本项目是一个简化的文件管理与审计平台，基于 **Flask + SQLite** 实现，支持用户身份验证、文件加密上传与下载、文件删除、日志审计等功能。
```

## 1.项目结构说明

ping32-lite/
 │
 ├── app.py                 # 应用入口，初始化 Flask 应用、注册蓝图
 ├── models.py              # 数据库模型定义，包括 User、AuditLog 等
 ├── auth.py                # 用户登录、注册与 token 验证逻辑
 ├── file_handler.py         # 文件相关 API 路由（上传、下载、删除、列表、日志）
 ├── templates/
 │   ├── index.html         # 前端首页页面，文件上传/下载/删除的界面
 │   └── audit.html         # 前端登录查看页面
 │   └── audit.html         # 前端登录查看页面
 ├── uploads/               # 文件加密上传保存目录
 ├── secret.key             # 对称加密密钥，生成后自动保存在本地
 ├── templates/ 
 │    └── db.sqlite3             # SQLite 数据库文件，保存用户和审计日志

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