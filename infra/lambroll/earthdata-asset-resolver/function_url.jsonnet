{
  Config: {
    AuthType: "AWS_IAM",
    Cors: {
      AllowOrigins: ["http://localhost:3000", "http://localhost:5173"],
      AllowMethods: ["POST", "OPTIONS"],
      AllowHeaders: ["Content-Type", "Authorization", "X-Amz-Date", "X-Amz-Security-Token"],
      MaxAge: 86400
    }
  },
  Permissions: [
    { Principal: "arn:aws:iam::086854724267:role/aws-service-role/sso.amazonaws.com/AWSServiceRoleForSSO" }
  ]
}
