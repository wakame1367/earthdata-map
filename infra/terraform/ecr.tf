module "ecr_resolver" {
  source       = "terraform-aws-modules/ecr/aws"
  name         = "earthdata-asset-resolver"
  force_delete = true
}
