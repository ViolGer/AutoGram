param(
  [ValidateSet("up","down","restart","logs","ps","smoke")]
  [string]$cmd = "up"
)

switch ($cmd) {
  "up" {
    docker compose up -d --build
    docker compose ps
    Write-Host "API:    http://127.0.0.1:8000/docs"
    Write-Host "Flower: http://127.0.0.1:5555"
  }
  "down" {
    docker compose down
  }
  "restart" {
    docker compose down
    docker compose up -d --build
    docker compose ps
  }
  "logs" {
    docker compose logs -f
  }
  "ps" {
    docker compose ps
  }
  "smoke" {
    curl http://127.0.0.1:8000/docs | Select-Object -First 5
  }
}
