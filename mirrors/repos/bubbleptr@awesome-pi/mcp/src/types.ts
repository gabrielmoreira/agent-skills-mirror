export type GuideKind = 'topic' | 'category' | 'package';

export type GuideLink = { kind: GuideKind; slug: string; title: string; piindexUrl: string };

export type PublicGuide = GuideLink & {
  titleZh: string;
  description: string;
  descriptionZh: string;
  packages: string[];
};

export type PublicCategory = {
  id: string;
  name: string;
  nameZh: string;
  kind: string;
  count: number;
  piindexUrl: string;
  guideUrl: string | null;
};

export type PublicKind = { id: string; name: string; nameZh: string; count: number; piindexUrl: string };

export type PublicPackage = {
  id: string;
  name: string;
  kind: string;
  kindName: string;
  kindNameZh: string;
  descriptions: { en: string[]; zh: string[] };
  categories: string[];
  searchText: string;
  projectUrl: string;
  repoUrl: string | null;
  npmPackage: string | null;
  npmUrl: string | null;
  install: string | null;
  stars: number | null;
  weeklyDownloads: number | null;
  weeklyTrendPercent: number | null;
  piindexUrl: string;
  directoryUrl: string;
  guideUrl: string | null;
  guides: GuideLink[];
};

export type PublicCatalog = {
  schemaVersion: number;
  site: string;
  source: string;
  statsGeneratedAt: string;
  kinds: PublicKind[];
  categories: PublicCategory[];
  guides: PublicGuide[];
  packages: PublicPackage[];
};

export type CatalogSource = 'file' | 'remote' | 'snapshot';

export type LoadedCatalog = { catalog: PublicCatalog; source: CatalogSource };
