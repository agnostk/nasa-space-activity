resource "aws_lightsail_container_service" "enrichment-service" {
  name  = "enrichment-service"
  power = "micro"
  scale = 1
}