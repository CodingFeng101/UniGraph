param([string]$Version = "1.0.0")

# 1. 构建
Write-Host "1) Building images ..."
docker compose build --no-cache

# 2. 打 tag
Write-Host "2) Tagging images ..."
docker tag unigraph-backend:latest unigraph/backend:$Version
docker tag unigraph-celery:latest  unigraph/celery:$Version
docker tag unigraph-frontend:latest unigraph/nginx:$Version

# 3. 导出为 tar
$tarName = "unigraph_{0}.tar" -f $Version
Write-Host "3) Exporting offline package $tarName ..."
docker save `
  unigraph/backend:$Version `
  unigraph/celery:$Version `
  unigraph/nginx:$Version `
  -o $tarName
