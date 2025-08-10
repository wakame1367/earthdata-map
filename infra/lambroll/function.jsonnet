{
  FunctionName: 'earthdata-asset-resolver',
  PackageType: 'Image',
  Role: '086854724267.dkr.ecr.ap-northeast-1.amazonaws.com/earthdata-asset-resolver',
  Code: {
    ImageUri: '{{ must_env `IMAGE_URI` }}'
  },
  MemorySize: 512,
  Timeout: 300,
  Environment: {
     Variables: {
      EDL_SECRET_ID: '{{ must_env `EDL_SECRET_ID` }}'
    }
  }
}