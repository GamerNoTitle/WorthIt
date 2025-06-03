# Worthit

我的物品买得有多值呢？

因为上了大学以后，我就在为我自己购买一些东西，这让我萌生了一个想法：如果这些东西，我一直用下去，那么每天使用它们的成本是多少呢？于是我就做了这么一个项目

## 开始使用

你需要准备一个 Notion 账号和一个 Vercel 账号 / 服务器 / 能跑容器的东西

### 复刻模板

打开这个 Notion 页面

https://gamernotitle.notion.site/WorthIt-2046dedbb716806f9927db492031cb9c

用自己的 Notion 账号复制一份，点击右上角的复制按钮就可以了

![](https://assets.bili33.top/img/Github/WorthIt/msedge_bnCMduOMds.png)

### 获取数据库 ID 和个人 API

复刻完成后，在自己的 Workspace 里面找到刚刚复刻的页面，展开它，找到下面的数据库

![](https://assets.bili33.top/img/Github/WorthIt/e9IkeC0Cps.png)

在上面链接处，就有自己的数据库 ID 了，举个例子

> https://www.notion.so/pesywu/207c22bc5364810d814af0cwodcnf8d5?v=207c22bc5364819f8a0a000c3e16fac1

这里的数据库 ID 为 `/` 以后，`?` 以前的内容，也就是 `207c22bc5364810d814af0cwodcnf8d5`

接着我们来获取我们自己的 API

访问 Notion 集成页面：https://www.notion.so/profile/integrations

在这个页面，我们添加一个新的集成，关联的工作空间需要选到这个数据库所在的工作空间，类型选择内部，记得在上面填入集成的名称

![](https://assets.bili33.top/img/Github/WorthIt/msedge_W9Y7EP0Nl7.png)

填完后点击创建，Notion 会带我们来到配置页面，我们首先需要在访问权限中添加需要访问的数据库

![](https://assets.bili33.top/img/Github/WorthIt/msedge_olETnZ3X5G.png)

然后我们再回到配置页面，获取我们要的 TOKEN，下面的勾勾不要动

![](https://assets.bili33.top/img/Github/WorthIt/msedge_wmdK6XM4Rk.png)

### 获取自己的用户名和密码

这里说的用户名和密码是在网站上登录使用的，用户名自己定就好了，主要是密码

密码可以在网站上进行 argon2 计算，也可以用 Linux 的 argon2 包

#### 使用网站进行计算

可以使用这个网站进行哈希计算 https://argon2.online/

注意参数的选择，应该要与我选择的一致

![](https://assets.bili33.top/img/Github/WorthIt/msedge_G0QysM1C7e.png)

生成后的哈希值就是 `WORTHIT_PASSWORD` 的值，你需要保留的是下面 `Output in Encoded Form` 的内容

#### 使用 Argon2 包计算

你首先需要安装 `argon2`

```bash
$ sudo apt install argon2
```

然后使用下面的命令

```bash
$ echo -n "password" | argon2 "$(openssl rand -base64 32)" -e -id -k 65540 -t 3 -p 4
```

注意把这里面的 `password` 换成自己的密码，得到的结果就是 `WORTHIT_PASSWORD` 的值

### 在 Vercel 上运行

首先 fork 本仓库，然后在 Vercel 中导入项目，导入时需要注意填写一下环境变量

|      变量名称      |            变量说明            | 默认值 |      必须       |                          备注                          |
| :----------------: | :----------------------------: | :----: | :-------------: | :----------------------------------------------------: |
|    NOTION_TOKEN    |       Notion 的集成密钥        |   -    |        ✓        |                           -                            |
| NOTION_DATABASE_ID |       Notion 的数据库 ID       |   -    |        ✓        |                           -                            |
|  WORTHIT_USERNAME  |        网站的登录用户名        |   -    |        ✓        |                           -                            |
|  WORTHIT_PASSWORD  |   网站登录密码的 argon2 哈希   |   -    |        ✓        |                           -                            |
|     SECRET_KEY     |   网站用于签发 JWT 的 token    |   -    | Vercel 部署必须 |               仅 Vercel 部署需要配置此项               |
| ENABLE_PUBLIC_VIEW | 允许非登录状态下查看到你的好物 | `true` |        ✕        | 设置为 `0` 或者 `false` 来禁用此项<br />否则都视为启用 |

![](https://assets.bili33.top/img/Github/WorthIt/msedge_PBZgBYFzRT.png)

填写完成后点击下面的 Deploy 部署就可以了
