# 使用官方的 Python 3.12 Slim 镜像作为基础
FROM python:3.12-slim

# 设置工作目录，后续所有命令都将在此目录下执行
WORKDIR /app

# 防止 Python 在安装过程中生成 .pyc 文件
ENV PYTHONDONTWRITEBYTECODE 1
# 不缓冲 Python 的 stdout 和 stderr，这样日志可以实时输出
ENV PYTHONUNBUFFERED 1

COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=5000

# 暴露 Flask 应用将运行的端口
EXPOSE 5000

CMD ["flask", "run"]