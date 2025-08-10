module "ecr_resolver" {
  source          = "terraform-aws-modules/ecr/aws"
  repository_name = "earthdata-asset-resolver"
}
