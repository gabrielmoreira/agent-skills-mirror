export type GatewayUpstreamResourceType =
  | "SCF"
  | "WEB_SCF"
  | "CBR"
  | "STATIC_STORE"
  | "LH"
  | string;

export type GatewayAccessUrlSource =
  | "gateway.custom"
  | "gateway.default";

export type GatewayRouteUrlCandidate = {
  Domain: string;
  Path?: string;
  IsDefault?: boolean;
  UpstreamResourceType?: string;
  UpstreamResourceName?: string;
};

export type RankedGatewayAccessUrl = {
  url: string;
  domain: string;
  path: string;
  isDefault: boolean;
  source: GatewayAccessUrlSource;
};

export type ResolveGatewayAccessUrlsResult = {
  accessUrl?: string;
  accessUrls: string[];
  accessUrlSource?: GatewayAccessUrlSource;
  routes: RankedGatewayAccessUrl[];
};

function normalizeAccessPath(path: string | undefined): string {
  if (!path) {
    return "/";
  }
  return path.startsWith("/") ? path : `/${path}`;
}

function buildHttpsUrl(domain: string, path: string): string {
  return `https://${domain}${normalizeAccessPath(path)}`;
}

/**
 * Rank gateway route URLs: custom domains (IsDefault !== true) before default domain.
 * Stable within each group; dedupe by full URL.
 */
export function rankGatewayAccessUrls(
  routes: GatewayRouteUrlCandidate[],
): RankedGatewayAccessUrl[] {
  const mapped = routes
    .filter((route) => Boolean(route.Domain))
    .map((route) => {
      const path = normalizeAccessPath(route.Path);
      const isDefault = route.IsDefault === true;
      return {
        url: buildHttpsUrl(route.Domain, path),
        domain: route.Domain,
        path,
        isDefault,
        source: (isDefault
          ? "gateway.default"
          : "gateway.custom") as GatewayAccessUrlSource,
      };
    });

  mapped.sort((a, b) => {
    if (a.isDefault === b.isDefault) {
      return 0;
    }
    return a.isDefault ? 1 : -1;
  });

  const seen = new Set<string>();
  const deduped: RankedGatewayAccessUrl[] = [];
  for (const item of mapped) {
    if (seen.has(item.url)) {
      continue;
    }
    seen.add(item.url);
    deduped.push(item);
  }
  return deduped;
}

export function flattenHttpServiceRoutes(result: {
  Domains?: Array<{
    Domain?: string;
    IsDefault?: boolean;
    Routes?: Array<Record<string, unknown>>;
  }>;
}): GatewayRouteUrlCandidate[] {
  return (result.Domains ?? []).flatMap((domainItem) =>
    (domainItem.Routes ?? []).map((route) => ({
      Domain: domainItem.Domain ?? "",
      IsDefault: domainItem.IsDefault,
      Path: typeof route.Path === "string" ? route.Path : undefined,
      UpstreamResourceType:
        typeof route.UpstreamResourceType === "string"
          ? route.UpstreamResourceType
          : undefined,
      UpstreamResourceName:
        typeof route.UpstreamResourceName === "string"
          ? route.UpstreamResourceName
          : undefined,
    })),
  );
}

export function filterRoutesByUpstream(
  routes: GatewayRouteUrlCandidate[],
  input: {
    upstreamResourceName: string;
    upstreamResourceTypes?: GatewayUpstreamResourceType[];
  },
): GatewayRouteUrlCandidate[] {
  const name = input.upstreamResourceName;
  const types = input.upstreamResourceTypes?.map((t) => String(t));
  return routes.filter((route) => {
    if (route.UpstreamResourceName !== name) {
      return false;
    }
    if (!types || types.length === 0) {
      return true;
    }
    return Boolean(
      route.UpstreamResourceType &&
        types.includes(String(route.UpstreamResourceType)),
    );
  });
}

export function toAccessUrlEnvelope(
  ranked: RankedGatewayAccessUrl[],
): ResolveGatewayAccessUrlsResult {
  if (ranked.length === 0) {
    return { accessUrls: [], routes: [] };
  }
  return {
    accessUrl: ranked[0].url,
    accessUrls: ranked.map((item) => item.url),
    accessUrlSource: ranked[0].source,
    routes: ranked,
  };
}

type CloudBaseManagerLike = {
  env: {
    describeHttpServiceRoute: (params: {
      EnvId: string;
      Limit?: number;
    }) => Promise<{
      Domains?: Array<{
        Domain?: string;
        IsDefault?: boolean;
        Routes?: Array<Record<string, unknown>>;
      }>;
    }>;
  };
};

/**
 * Best-effort lookup of gateway access URLs for an upstream resource.
 * Never throws — returns empty lists on failure.
 */
export async function resolveGatewayAccessUrls(input: {
  envId: string;
  upstreamResourceName: string;
  upstreamResourceTypes?: GatewayUpstreamResourceType[];
  getManager: () => Promise<CloudBaseManagerLike>;
}): Promise<ResolveGatewayAccessUrlsResult> {
  try {
    const manager = await input.getManager();
    const result = await manager.env.describeHttpServiceRoute({
      EnvId: input.envId,
      Limit: 1000,
    });
    const flattened = flattenHttpServiceRoutes(result);
    const matched = filterRoutesByUpstream(flattened, {
      upstreamResourceName: input.upstreamResourceName,
      upstreamResourceTypes: input.upstreamResourceTypes,
    });
    return toAccessUrlEnvelope(rankGatewayAccessUrls(matched));
  } catch {
    return { accessUrls: [], routes: [] };
  }
}

/**
 * Merge ranked gateway URLs with a resource-native fallback URL.
 * Gateway custom/default always win over the fallback when present.
 */
export function preferGatewayOrFallback(input: {
  gateway: ResolveGatewayAccessUrlsResult;
  fallbackUrl?: string;
  fallbackSource?: string;
}): {
  accessUrl?: string;
  accessUrls: string[];
  accessUrlSource?: string;
} {
  if (input.gateway.accessUrl) {
    const urls = [...input.gateway.accessUrls];
    if (
      input.fallbackUrl &&
      !urls.includes(input.fallbackUrl)
    ) {
      urls.push(input.fallbackUrl);
    }
    return {
      accessUrl: input.gateway.accessUrl,
      accessUrls: urls,
      accessUrlSource: input.gateway.accessUrlSource,
    };
  }

  if (input.fallbackUrl) {
    return {
      accessUrl: input.fallbackUrl,
      accessUrls: [input.fallbackUrl],
      accessUrlSource: input.fallbackSource,
    };
  }

  return { accessUrls: [] };
}
