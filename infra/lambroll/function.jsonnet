{
  FunctionName: 'fit-energy-scraper',
  PackageType: 'Image',
  Role: 'arn:aws:iam::086854724267:role/fit-energy-platform-lambroll-lambda-role',
  Code: {
    ImageUri: '{{ must_env `IMAGE_URI` }}'
  },
  MemorySize: 512,
  Timeout: 300,
  Environment: {
    Variables: {
      S3_BUCKET: '{{ must_env `S3_BUCKET` }}'
    }
  }
}