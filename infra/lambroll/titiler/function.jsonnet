{
  FunctionName: 'titiler',
  PackageType: 'Image',
  Role: 'arn:aws:iam::086854724267:role/earthdata-asset-resolver-role',
  Code: {
    ImageUri: '{{ must_env `IMAGE_URI` }}'
  },
  MemorySize: 512,
  Timeout: 300,
  Environment: {
  }
}