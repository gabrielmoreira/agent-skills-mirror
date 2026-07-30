import { describe, expect, it } from "vitest";
import {
  filterRoutesByUpstream,
  flattenHttpServiceRoutes,
  preferGatewayOrFallback,
  rankGatewayAccessUrls,
  toAccessUrlEnvelope,
} from "./gateway-access-urls.js";

describe("gateway-access-urls", () => {
  it("ranks custom domain URLs before default domain URLs", () => {
    const ranked = rankGatewayAccessUrls([
      {
        Domain: "env-test.service.tcloudbase.com",
        Path: "/api",
        IsDefault: true,
        UpstreamResourceName: "hello",
        UpstreamResourceType: "WEB_SCF",
      },
      {
        Domain: "api.example.com",
        Path: "/api",
        IsDefault: false,
        UpstreamResourceName: "hello",
        UpstreamResourceType: "WEB_SCF",
      },
    ]);

    expect(ranked.map((item) => item.url)).toEqual([
      "https://api.example.com/api",
      "https://env-test.service.tcloudbase.com/api",
    ]);
    expect(ranked[0].source).toBe("gateway.custom");
    expect(ranked[1].source).toBe("gateway.default");
  });

  it("dedupes identical URLs and normalizes paths", () => {
    const ranked = rankGatewayAccessUrls([
      {
        Domain: "api.example.com",
        Path: "api",
        IsDefault: false,
      },
      {
        Domain: "api.example.com",
        Path: "/api",
        IsDefault: false,
      },
    ]);

    expect(ranked).toHaveLength(1);
    expect(ranked[0].url).toBe("https://api.example.com/api");
  });

  it("returns empty envelope when no routes match", () => {
    expect(toAccessUrlEnvelope([])).toEqual({
      accessUrls: [],
      routes: [],
    });
  });

  it("flattens and filters routes by upstream type and name", () => {
    const flattened = flattenHttpServiceRoutes({
      Domains: [
        {
          Domain: "api.example.com",
          IsDefault: false,
          Routes: [
            {
              Path: "/run",
              UpstreamResourceType: "CBR",
              UpstreamResourceName: "my-service",
            },
            {
              Path: "/fn",
              UpstreamResourceType: "WEB_SCF",
              UpstreamResourceName: "hello",
            },
          ],
        },
      ],
    });

    const matched = filterRoutesByUpstream(flattened, {
      upstreamResourceName: "my-service",
      upstreamResourceTypes: ["CBR"],
    });

    expect(matched).toHaveLength(1);
    expect(matched[0].Path).toBe("/run");
  });

  it("prefers gateway URLs over resource-native fallback", () => {
    const preferred = preferGatewayOrFallback({
      gateway: {
        accessUrl: "https://api.example.com/app",
        accessUrls: ["https://api.example.com/app"],
        accessUrlSource: "gateway.custom",
        routes: [],
      },
      fallbackUrl: "https://env.tcloudbaseapp.com/app/",
      fallbackSource: "hosting.staticDomain",
    });

    expect(preferred).toEqual({
      accessUrl: "https://api.example.com/app",
      accessUrls: [
        "https://api.example.com/app",
        "https://env.tcloudbaseapp.com/app/",
      ],
      accessUrlSource: "gateway.custom",
    });
  });

  it("falls back to resource-native URL when gateway has no match", () => {
    const preferred = preferGatewayOrFallback({
      gateway: { accessUrls: [], routes: [] },
      fallbackUrl: "https://svc.run.tcloudbase.com",
      fallbackSource: "cloudrun.defaultDomain",
    });

    expect(preferred).toEqual({
      accessUrl: "https://svc.run.tcloudbase.com",
      accessUrls: ["https://svc.run.tcloudbase.com"],
      accessUrlSource: "cloudrun.defaultDomain",
    });
  });
});
