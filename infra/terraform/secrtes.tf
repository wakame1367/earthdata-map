resource "aws_secretsmanager_secret" "edl_token" {
  name = "earthdata/edl-token"
}
# 値の投入は CLI か CI で:
# aws secretsmanager put-secret-value --secret-id earthdata/edl-token --secret-string '{"token":"<EDL_TOKEN>"}'
