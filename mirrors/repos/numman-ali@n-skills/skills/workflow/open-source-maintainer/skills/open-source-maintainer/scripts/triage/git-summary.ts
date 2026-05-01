import { execFileSync } from 'node:child_process';

export type GitSummary = {
  status: string;
  diffStat: string;
  untracked: string[];
};

export function getGitSummary(): GitSummary | null {
  try {
    const status = execFileSync('git', ['status', '-sb'], { encoding: 'utf8' }).trim();
    const diffStat = execFileSync('git', ['diff', '--stat', '--', '.github/maintainer'], { encoding: 'utf8' }).trim();
    const porcelain = execFileSync('git', ['status', '--porcelain', '--', '.github/maintainer'], { encoding: 'utf8' }).trim();
    const untracked = porcelain
      ? porcelain.split('\n').filter((line) => line.startsWith('?? ')).map((line) => line.slice(3))
      : [];
    return { status, diffStat, untracked };
  } catch {
    return null;
  }
}
