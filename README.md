# PyBlog
![license](https://img.shields.io/github/license/mashape/apistatus.svg) ![PyPI - Python 3.5](https://img.shields.io/pypi/pyversions/Django.svg) ![GitHub repo size in bytes](https://img.shields.io/github/repo-size/badges/shields.svg)

## 运行环境
+ Windows / Linux / macOS and so on...
+ python 3
+ MySQL 5+

## 安装说明
首先在MySQL中创建一个数据库，注意同时设置了字符集为utf8以支持中文。以数据库用户root:root为例:
```
~ mysql -uroot -proot -e "create database pyblog  default character set utf8;"
```

安装过程
```
~ git clone https://github.com/CHYbeta/PyBlog.git
~ cd PyBlog/
~ python3 -m pip install -r requirements.txt
~ python3 manager.py create_db
~ python3 manager.py create_user
~ python3 manager.py runserver
```

打开浏览器： http://127.0.0.1:5000/ 

默认后台地址： http://127.0.0.1:5000/login

默认超级管理员账号： admin@pyblog.com

默认超级管理员密码： admin

## 界面预览
主界面
![](preview_pic/index.png)

文章列表
![](preview_pic/posts.png)

文章查看
![](preview_pic/postview.png)

类别查看
![](preview_pic/categories.png)

后台登录
![](preview_pic/login.png)

超级管理员主界面
![](preview_pic/admin_index.png)

普通管理员主界面
![](preview_pic/normal_user.png)

后台用户管理
![](preview_pic/user_list.png)

后台文章管理
![](preview_pic/post_list.png)

# Contributors
+ [@Jackfkchan](https://github.com/Jackfkchan)
+ [@sun3et](https://github.com/initlisk)