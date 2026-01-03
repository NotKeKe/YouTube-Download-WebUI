# 一階
FROM node:20-alpine AS frontend-builder

WORKDIR /build
# copy package.json to use Docker layer cache
COPY front/package.json front/package-lock.json* ./
RUN npm install

# copy source code and build
COPY front/ .
RUN npm run build


# 二階
FROM python:3.14.2-alpine

# 時間設定
RUN ln -sf /usr/share/zoneinfo/Asia/Taipei /etc/localtime \
    && echo "Asia/Taipei" > /etc/timezone

# 安裝 uv
RUN pip install uv --no-cache-dir

# 安裝 ffmpeg, opus 依賴
RUN apk add --no-cache ffmpeg

WORKDIR /app

# 環境變數
ENV RUNNING_IN_DOCKER=true

# 先複製一次，如果使用者有 .env 的話會再覆蓋掉
COPY . .

# 複製一階的東西到二階
COPY --from=frontend-builder /build/dist ./front/dist

RUN uv sync

CMD ["uv", "run", "main.py"]