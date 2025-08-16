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
    { Principal: "arn:aws:iam::086854724267:role/aws-reserved/sso.amazonaws.com/ap-northeast-1/AWSReservedSSO_AdministratorAccess_26a7ba43d0e26c41" }
  ]
}
