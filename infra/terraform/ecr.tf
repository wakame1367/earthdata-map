resource "aws_ecr_repository" "app" {
  name   = "earthdata-asset-resolver"
  region = aws.uswest2
  image_scanning_configuration {
    scan_on_push = true
  }
}
