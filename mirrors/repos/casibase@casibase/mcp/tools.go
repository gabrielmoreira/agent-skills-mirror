// Copyright 2026 The OpenAgent Authors. All Rights Reserved.
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//      http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

package mcp

import (
	"context"
	"fmt"
	"time"

	"github.com/ThinkInAIXYZ/go-mcp/client"
	"github.com/ThinkInAIXYZ/go-mcp/protocol"
	"github.com/ThinkInAIXYZ/go-mcp/transport"
)

// GetToolsFromURL connects to an HTTP-based MCP server and returns its tool list.
// Always uses StreamableHTTP transport (the current MCP standard); when token is
// non-empty it is sent as a Bearer Authorization header.
func GetToolsFromURL(url, token string) ([]*protocol.Tool, error) {
	var tr transport.ClientTransport
	var err error

	if token != "" {
		tr, err = transport.NewStreamableHTTPClientTransport(url,
			transport.WithStreamableHTTPClientOptionHeader(map[string]string{
				"Authorization": "Bearer " + token,
			}),
		)
	} else {
		tr, err = transport.NewStreamableHTTPClientTransport(url)
	}
	if err != nil {
		return nil, fmt.Errorf("mcp: create transport for %s: %w", url, err)
	}

	cli, err := client.NewClient(tr)
	if err != nil {
		return nil, fmt.Errorf("mcp: create client for %s: %w", url, err)
	}
	defer cli.Close()

	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
	defer cancel()

	list, err := cli.ListTools(ctx)
	if err != nil {
		return nil, fmt.Errorf("mcp: list tools from %s: %w", url, err)
	}
	return list.Tools, nil
}
