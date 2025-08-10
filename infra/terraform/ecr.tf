resource "aws_ecr_repository" "app" {
  name = "earthdata-asset-resolver"
  image_scanning_configuration {
    scan_on_push = true
  }
}
