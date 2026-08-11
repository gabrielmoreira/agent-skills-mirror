# Error Logging Examples

Use these examples as mapping patterns, not as a fixed event-key catalog.

## Catch With A Real Error

Bad:

```ts
catch (error) {
	logger.error(`Connection failed: ${(error as Error).message}`)
}
```

Good:

```ts
catch (error) {
	logger.error({
		eventKey: "voice_worker_connection_failed",
		errorKind: "network",
		error,
		message: "[Proxy] Connection failed",
	})
}
```

Keep the original Error. Do not replace it with `error.message`.

## Preserve Raw Parsing Evidence With A Bound

Bad:

```ts
logger.error({
	eventKey: "drag_logger_parse_failed",
	errorKind: "parse",
	error: data.error,
	message: "[DragLogger] 拖拽数据解析失败",
	context: { rawDataLength: data.rawData?.length },
})
```

Good:

```ts
logger.error({
	eventKey: "drag_logger_parse_failed",
	errorKind: "parse",
	error: data.error,
	message: "[DragLogger] 拖拽数据解析失败",
	context: {
		sessionId: this.sessionId,
		time: log.time,
		// 原始数据是解析失败的关键依据；沿用受控长度避免无界上报。
		rawData: data.rawData?.substring(0, 200),
		rawDataLength: data.rawData?.length,
	},
})
```

Do not keep only a length when the bounded raw value is required to diagnose parsing.

## Preserve Historical Context

Bad:

```ts
logger.error({
	eventKey: "fallback_auto_model_failed",
	errorKind: "invalid_state",
	message: "Fallback to auto model",
	context: { modeCount: modeList.length },
})
```

If the historical call included the model list and other fields, first determine which values are bounded and necessary. Do not reduce the payload to a count solely for neatness. Preserve the original diagnostic fields unless a concrete size or sensitivity boundary applies.

## Preserve Iframe Link Information

Bad:

```ts
context: buildMessageLogContext(event, messageType, {
	isExpectedSource,
	isAllowedType,
	autoEdit,
})
```

Good:

```ts
// 保留历史链接信息，便于定位 iframe 跳转失败。
context: buildMessageLogContext(event, messageType, {
	isExpectedSource,
	isAllowedType,
	href,
	autoEdit,
})
```

Do not delete `href` automatically. Inspect whether it contains credentials or sensitive query values and apply the narrowest necessary treatment.

## Map A Typed Callback Correctly

Given:

```ts
onError?: (errorType: string, error: unknown) => void
```

Bad:

```ts
onError={(...args) => {
	const error = args.find((item) => item instanceof Error) ?? args[args.length - 1]
	logger.error({
		eventKey: "private_deployment_login_failed",
		errorKind: "permission",
		error,
		context: { arguments: args },
	})
}}
```

Good:

```ts
onError={(errorType, error) => {
	// 回调分别提供业务错误标识和错误值，映射到 context 与顶层 error。
	logger.error({
		eventKey: "private_deployment_login_failed",
		errorKind: "permission",
		error,
		message: "privateDeploymentLoginError",
		context: { errorType },
	})
}}
```

Read the callback type instead of guessing which rest argument is the error.

## Preserve A Shared Context Builder

Given a context builder that already supplies recording state:

```ts
private createLogContext(extra = {}) {
	return {
		recordingId: this.recordingId,
		chunkIndex: this.chunkIndex,
		status: this.status,
		isRecording: this.isRecording,
		isConnected: this.isConnected,
		networkStatus: this.networkStatus,
		retryCount: this.retryCount,
		...extra,
	}
}
```

Use:

```ts
logger.error({
	eventKey: "network_recording_start_failed",
	errorKind: "network",
	error,
	message: "网络异常：录音启动失败",
	context: this.createLogContext(),
})
```

Do not pass `message` or `error` into the context builder when they are already top-level fields. Do not discard the builder's public diagnostics.

## Do Not Change Unrelated Business Helpers

For a logging-only task, do not add or rewrite helpers such as credential sanitizers, request transformers, model selectors, state normalization, or URL construction unless the logging call cannot be made safe without the smallest targeted change.

Bad scope:

```text
change logger.error call
+ rewrite sanitizeTemporaryCredential
+ change credential type detection
+ change upload behavior
```

Good scope:

```text
change logger.error call
+ map existing safe values to error/message/context
+ add one comment explaining a non-obvious exclusion
```

## Adapter Pattern

An adapter should forward the structured contract and only enrich its owned context:

```ts
error(input: StructuredErrorInput): void {
	logger.error({
		...input,
		context: {
			sessionId: this.sessionId,
			...input.context,
		},
	})
}
```

Do not rebuild the message, stringify the Error, replace the event key, or drop caller context.

## ErrorBoundary Pattern

```ts
logger.error({
	eventKey: "message_render_failed",
	errorKind: "render",
	error,
	message: "消息渲染失败",
	context: {
		componentStack: errorInfo.componentStack,
	},
})
```

Keep `componentStack` as diagnostic context. Keep the original Error at top level.
