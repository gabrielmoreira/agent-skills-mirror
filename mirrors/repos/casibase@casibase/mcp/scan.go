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
	"encoding/binary"
	"fmt"
	"net"
	"net/http"
	"slices"
	"strconv"
	"strings"
	"sync"
	"time"
)

const (
	defaultScanTimeoutMs      = 1200
	defaultScanMaxConcurrency = 32
	MaxScanHosts              = 1024
)

var (
	defaultScanPorts = []int{3000, 8080, 80}
	defaultScanPaths = []string{"/", "/mcp", "/sse", "/mcp/sse"}
)

type InnerMcpServer struct {
	Host string `json:"host"`
	Port int    `json:"port"`
	Path string `json:"path"`
	Url  string `json:"url"`
}

type ScanIntranetResult struct {
	CIDR         []string          `json:"cidr"`
	ScannedHosts int               `json:"scannedHosts"`
	OnlineHosts  []string          `json:"onlineHosts"`
	Servers      []*InnerMcpServer `json:"servers"`
}

// ScanIntranetServers probes all IPv4 hosts in cidr for active MCP endpoints.
// ports and paths may be empty, in which case defaults are used.
func ScanIntranetServers(cidr, ports, paths []string) (*ScanIntranetResult, error) {
	hosts, err := parseScanTargets(cidr, MaxScanHosts)
	if err != nil {
		return nil, err
	}

	timeout := sanitizeTimeout(0, defaultScanTimeoutMs, 10000)
	concurrency := sanitizeConcurrency(0, defaultScanMaxConcurrency, 256)
	resolvedPorts := sanitizePorts(ports, defaultScanPorts)
	resolvedPaths := sanitizePaths(paths, defaultScanPaths)

	httpClient := &http.Client{
		Timeout: timeout,
		CheckRedirect: func(_ *http.Request, _ []*http.Request) error {
			return http.ErrUseLastResponse
		},
	}

	ctx, cancel := context.WithTimeout(context.Background(), time.Minute)
	defer cancel()

	onlineHostSet := map[string]struct{}{}
	serverMap := map[string]*InnerMcpServer{}
	mu := sync.Mutex{}
	wg := sync.WaitGroup{}
	sem := make(chan struct{}, concurrency)

	for _, host := range hosts {
		h := host.String()
		wg.Add(1)
		go func() {
			defer wg.Done()
			select {
			case sem <- struct{}{}:
			case <-ctx.Done():
				return
			}
			defer func() { <-sem }()

			isOnline, servers := probeHost(ctx, httpClient, h, resolvedPorts, resolvedPaths, timeout)
			if !isOnline {
				return
			}
			mu.Lock()
			onlineHostSet[h] = struct{}{}
			for _, s := range servers {
				serverMap[s.Url] = s
			}
			mu.Unlock()
		}()
	}
	wg.Wait()

	onlineHosts := make([]string, 0, len(onlineHostSet))
	for h := range onlineHostSet {
		onlineHosts = append(onlineHosts, h)
	}
	slices.Sort(onlineHosts)

	servers := make([]*InnerMcpServer, 0, len(serverMap))
	for _, s := range serverMap {
		servers = append(servers, s)
	}
	slices.SortFunc(servers, func(a, b *InnerMcpServer) int {
		if a.Url < b.Url {
			return -1
		}
		if a.Url > b.Url {
			return 1
		}
		return 0
	})

	return &ScanIntranetResult{
		CIDR:         cidr,
		ScannedHosts: len(hosts),
		OnlineHosts:  onlineHosts,
		Servers:      servers,
	}, nil
}

func isIntranetIP(ipStr string) bool {
	ip := net.ParseIP(ipStr)
	if ip == nil {
		return false
	}
	ipv4 := ip.To4()
	if ipv4 == nil {
		return false
	}
	for _, cidr := range []string{"10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16", "127.0.0.0/8"} {
		_, ipNet, _ := net.ParseCIDR(cidr)
		if ipNet != nil && ipNet.Contains(ipv4) {
			return true
		}
	}
	return false
}

func parseScanTargets(targets []string, maxHosts int) ([]net.IP, error) {
	hostSet := map[uint32]struct{}{}
	hosts := make([]net.IP, 0)

	addHost := func(ipv4 net.IP) error {
		val := binary.BigEndian.Uint32(ipv4)
		if _, ok := hostSet[val]; ok {
			return nil
		}
		if len(hosts) >= maxHosts {
			return fmt.Errorf("scan targets exceed max %d hosts", maxHosts)
		}
		hostSet[val] = struct{}{}
		h := make(net.IP, net.IPv4len)
		copy(h, ipv4)
		hosts = append(hosts, h)
		return nil
	}

	for _, target := range targets {
		target = strings.TrimSpace(target)
		if target == "" {
			continue
		}
		if ip := net.ParseIP(target); ip != nil {
			ipv4 := ip.To4()
			if ipv4 == nil {
				return nil, fmt.Errorf("only IPv4 is supported: %s", target)
			}
			if !isIntranetIP(ipv4.String()) {
				return nil, fmt.Errorf("target must be an intranet address: %s", target)
			}
			if err := addHost(ipv4); err != nil {
				return nil, err
			}
			continue
		}
		cidrHosts, err := parseCIDRHosts(target, maxHosts)
		if err != nil {
			return nil, err
		}
		for _, h := range cidrHosts {
			if !isIntranetIP(h.String()) {
				return nil, fmt.Errorf("target must be an intranet address: %s", target)
			}
			if err = addHost(h.To4()); err != nil {
				return nil, err
			}
		}
	}

	if len(hosts) == 0 {
		return nil, fmt.Errorf("at least one CIDR or IP target is required")
	}
	return hosts, nil
}

func parseCIDRHosts(cidr string, maxHosts int) ([]net.IP, error) {
	baseIP, ipNet, err := net.ParseCIDR(cidr)
	if err != nil {
		return nil, err
	}
	ipv4 := baseIP.To4()
	if ipv4 == nil {
		return nil, fmt.Errorf("only IPv4 CIDR is supported")
	}
	ones, bits := ipNet.Mask.Size()
	hostBits := bits - ones
	if hostBits >= 63 {
		return nil, fmt.Errorf("CIDR range is too large")
	}
	total := uint64(1) << hostBits
	if total > uint64(maxHosts)+2 {
		return nil, fmt.Errorf("CIDR range exceeds max %d hosts", maxHosts)
	}
	start := binary.BigEndian.Uint32(ipv4.Mask(ipNet.Mask))
	end := start + uint32(total) - 1
	hosts := make([]net.IP, 0, int(total))
	for v := start; v <= end; v++ {
		if total > 2 && (v == start || v == end) {
			continue
		}
		candidate := make(net.IP, net.IPv4len)
		binary.BigEndian.PutUint32(candidate, v)
		if ipNet.Contains(candidate) {
			hosts = append(hosts, candidate)
		}
	}
	if len(hosts) == 0 {
		return nil, fmt.Errorf("CIDR has no usable hosts: %s", cidr)
	}
	return hosts, nil
}

func probeHost(ctx context.Context, httpClient *http.Client, host string, ports []int, paths []string, timeout time.Duration) (bool, []*InnerMcpServer) {
	if !isIntranetIP(host) {
		return false, nil
	}
	dialer := &net.Dialer{Timeout: timeout}
	isOnline := false
	var servers []*InnerMcpServer

	for _, port := range ports {
		address := net.JoinHostPort(host, strconv.Itoa(port))
		conn, err := dialer.DialContext(ctx, "tcp", address)
		if err != nil {
			continue
		}
		_ = conn.Close()
		isOnline = true

		for _, path := range paths {
			if s, ok := probeMcpEndpoint(ctx, httpClient, host, port, path); ok {
				servers = append(servers, s)
			}
		}
	}
	return isOnline, servers
}

func probeMcpEndpoint(ctx context.Context, httpClient *http.Client, host string, port int, path string) (*InnerMcpServer, bool) {
	fullURL := fmt.Sprintf("http://%s%s", net.JoinHostPort(host, strconv.Itoa(port)), path)
	req, err := http.NewRequestWithContext(ctx, http.MethodPost, fullURL, nil)
	if err != nil {
		return nil, false
	}
	resp, err := httpClient.Do(req)
	if err != nil {
		return nil, false
	}
	defer func() { _ = resp.Body.Close() }()

	if resp.StatusCode == http.StatusNotFound {
		return nil, false
	}
	return &InnerMcpServer{Host: host, Port: port, Path: path, Url: fullURL}, true
}

func sanitizeTimeout(ms, defaultMs, maxMs int) time.Duration {
	if ms <= 0 {
		ms = defaultMs
	}
	if ms > maxMs {
		ms = maxMs
	}
	return time.Duration(ms) * time.Millisecond
}

func sanitizeConcurrency(n, def, max int) int {
	if n <= 0 {
		n = def
	}
	if n > max {
		n = max
	}
	return n
}

func sanitizePorts(inputs []string, defaults []int) []int {
	if len(inputs) == 0 {
		return append([]int{}, defaults...)
	}
	portSet := map[int]struct{}{}
	result := make([]int, 0)
	for _, s := range inputs {
		s = strings.TrimSpace(s)
		if s == "" {
			continue
		}
		p, err := strconv.Atoi(s)
		if err != nil || p <= 0 || p > 65535 {
			continue
		}
		if _, ok := portSet[p]; ok {
			continue
		}
		portSet[p] = struct{}{}
		result = append(result, p)
	}
	if len(result) == 0 {
		return append([]int{}, defaults...)
	}
	return result
}

func sanitizePaths(inputs []string, defaults []string) []string {
	if len(inputs) == 0 {
		return append([]string{}, defaults...)
	}
	pathSet := map[string]struct{}{}
	result := make([]string, 0)
	for _, p := range inputs {
		p = strings.TrimSpace(p)
		if p == "" {
			continue
		}
		if !strings.HasPrefix(p, "/") {
			p = "/" + p
		}
		if _, ok := pathSet[p]; ok {
			continue
		}
		pathSet[p] = struct{}{}
		result = append(result, p)
	}
	if len(result) == 0 {
		return append([]string{}, defaults...)
	}
	return result
}
