// CloudBase MCP Server Library
export {
  createCloudBaseMcpServer,
  getDefaultServer,
  type McpServer,
  type ExtendedMcpServer,
  type CloudBaseRegisterToolConfig,
  StdioServerTransport,
  telemetryReporter,
  reportToolkitLifecycle,
  reportToolCall,
  info,
  error,
  warn
} from "./server.js";

export type { Tool, ToolAnnotations } from "./utils/tool-wrapper.js";

export type {
  UploadFileParams,
  ListFilesParams,
  DeleteFileParams,
  GetFileInfoParams,
  ToolResponse,
  DataModelField,
  DataModelSchema,
  DataModel,
  CloudBaseOptions,
  FunctionDeployOverrides,
  PluginOptions,
  CloudApiRequestFn,
  MsgPushAction,
  MsgPushQbaseResponse,
  MsgPushOverrides,
} from "./types.js";

export { getLoginState, logout } from "./auth.js";
export type {
  AuthFlowMode,
  AuthOptions,
  DeviceFlowAuthInfo,
  EnsureLoginOptions,
} from "./auth.js";

export { isCloudMode, enableCloudMode, getCloudModeStatus, shouldRegisterTool } from "./utils/cloud-mode.js";

/**
 * 环境绑定槽。外部宿主（自己起 transport 的那种）要上报真实的 envId，
 * 就得在自己的一次 run 里跑 server 的消息处理，否则上报恒为 `default`。
 */
export { ENV_SOURCES, runWithEnvSlot } from "./utils/env-binding.js";
export type { EnvBinding, EnvSlot, EnvSource } from "./utils/env-binding.js";

export {
  getCloudBaseManager,
  getEnvId,
  resetCloudBaseManagerCache,
  createCloudBaseManagerWithOptions,
  envManager
} from "./cloudbase-manager.js";

export { simplifyEnvList } from "./tools/env.js";

export { RAW_IDE_FILE_MAPPINGS } from "./tools/setup.js";
export { warmupHostedResources } from "./tools/rag.js";
export {
  handleHostedMcpRequest,
  HOSTED_CLIENT_INFO_CACHE_CAPACITY,
  HOSTED_CLIENT_INFO_CACHE_TTL_MS,
} from "./hosted/index.js";
export type {
  CloudBaseServerOptions,
  HostedCloudBaseOptions,
  HostedMcpLogEvent,
  HostedMcpRequestInput,
  HostedClientInfoRecord,
} from "./hosted/index.js";

// Export runtime constants for multi-language support
export {
  SUPPORTED_RUNTIMES,
  ALL_SUPPORTED_RUNTIMES,
  DEFAULT_RUNTIME,
  RECOMMENDED_RUNTIMES,
  formatRuntimeList,
  SUPPORTED_NODEJS_RUNTIMES,
  DEFAULT_NODEJS_RUNTIME,
  validateTimerCron,
} from "./tools/functions.js";
