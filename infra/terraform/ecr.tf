resource "aws_ecr_repository" "earthdata_asset_resolver" {
  name     = "earthdata-asset-resolver"
  provider = aws.uswest2
  image_scanning_configuration {
    scan_on_push = true
  }
}

resource "aws_ecr_repository" "titiler" {
  name     = "titiler"
  provider = aws.uswest2
  image_scanning_configuration {
    scan_on_push = true
  }
}
