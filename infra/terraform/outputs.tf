output "resolver_lambda_role_arn" {
  value = aws_iam_role.resolver.arn
}

output "titiler_ecr_url" {
  value = aws_ecr_repository.titiler.repository_url
}

output "earthdata_asset_resolver_ecr_url" {
  value = aws_ecr_repository.earthdata_asset_resolver.repository_url
}
