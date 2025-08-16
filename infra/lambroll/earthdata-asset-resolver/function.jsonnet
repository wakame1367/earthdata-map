{
  FunctionName: 'earthdata-asset-resolver',
  PackageType: 'Image',
  Role: 'arn:aws:iam::086854724267:role/earthdata-asset-resolver-role',
  Code: {
    ImageUri: '{{ must_env `IMAGE_URI` }}'
  },
  MemorySize: 512,
  Timeout: 300,
  Environment: {
     Variables: {
      EDL_SECRET_ID: '{{ must_env `EDL_SECRET_ID` }}',
      TITILER_BASE: 'https://r7lbmsdicrfgcl2iwnk73ppr6e0wxekp.lambda-url.us-west-2.on.aws'
    }
  }
}