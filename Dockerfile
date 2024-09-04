FROM python:3.11.2-bullseye

# 暴露 Render 預期的端口
EXPOSE 8080

# 設置工作目錄
WORKDIR /phoenixc2

# 複製所有文件到工作目錄
COPY . .

# 確認 Python 版本
RUN python --version

# 安裝 Poetry，這裡禁用 pip 的版本檢查來加速
RUN pip install poetry --disable-pip-version-check

# 使用 Poetry 安裝依賴項
RUN poetry install

# 安裝 Golang (如果你的應用需要 Go)
RUN apt update && apt install -y golang-go

# 設置環境變量，以便使用 Render 平台的 PORT 環境變量
ENV PORT=8080

# 執行 Poetry 並啟動 Phoenix C2
ENTRYPOINT ["poetry", "run"]

# 設置默認命令來啟動 Phoenix C2，並綁定到 0.0.0.0 和 PORT
CMD ["phserver", "--host", "0.0.0.0", "--port", "$PORT"]
