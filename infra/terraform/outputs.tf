output "resolver_lambda_role_arn" {
  value = aws_iam_role.resolver.arn
}

output "ecr_url" {
  value = aws_ecr_repository.app.repository_url
}
