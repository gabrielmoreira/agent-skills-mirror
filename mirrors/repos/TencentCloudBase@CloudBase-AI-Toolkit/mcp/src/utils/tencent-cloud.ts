import {
    SITE_REGION_MAP,
    getSite,
    isSiteId,
    normalizeSite,
    resolveSite,
    resolveSiteAndRegion,
} from './site-map.js';
import type { SiteId, SiteDefinition, SiteResolution } from './site-map.js';

const REGION = {
    SHANGHAI: 'ap-shanghai',
    SINGAPORE: 'ap-singapore',
} as const;

export type Region = typeof REGION[keyof typeof REGION];

export type { SiteId, SiteDefinition, SiteResolution };
export { SITE_REGION_MAP, getSite, isSiteId, normalizeSite, resolveSite, resolveSiteAndRegion };

/**
 * @deprecated 使用 `getSite`/`resolveSite` 替代。region 与 site 不再 1:1 绑定，
 * 此处保留兼容名，内部按映射表解析（ap-singapore 歧义时按 intl 处理，兼容既有国际站行为）。
 */
export const isInternationalRegion = (region: string | undefined): boolean =>
    resolveSite(region) === 'intl';

export function isValidRegion(region: string): region is Region {
    return Object.values(REGION).includes(region as Region);
}
