export async function checkedShader(device: GPUDevice, label: string, code: string) {
  const module = device.createShaderModule({ label, code })
  const info = await module.getCompilationInfo()
  const errors = info.messages.filter((message) => message.type === 'error')
  if (errors.length) throw new Error(`${label}: ${errors.map((message) => `${message.lineNum}:${message.linePos} ${message.message}`).join('\n')}`)
  return module
}
