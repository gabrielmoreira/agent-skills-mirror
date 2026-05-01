import { execFileSync } from 'node:child_process';

import { GhIssueNode, GhPullRequestNode } from './types';

export const ISSUE_QUERY = `
query($owner: String!, $repo: String!, $cursor: String) {
  repository(owner: $owner, name: $repo) {
    issues(first: 50, states: OPEN, after: $cursor, orderBy: {field: UPDATED_AT, direction: DESC}) {
      nodes {
        number
        title
        body
        url
        createdAt
        updatedAt
        author { login }
        labels(first: 50) { nodes { name } }
        assignees(first: 20) { nodes { login } }
        comments(first: 100) {
          totalCount
          nodes {
            url
            body
            createdAt
            author { login }
            authorAssociation
            reactionGroups { content users { totalCount } }
          }
        }
      }
      pageInfo { hasNextPage endCursor }
    }
  }
}
`;

export const PR_QUERY = `
query($owner: String!, $repo: String!, $cursor: String) {
  repository(owner: $owner, name: $repo) {
    pullRequests(first: 50, states: OPEN, after: $cursor, orderBy: {field: UPDATED_AT, direction: DESC}) {
      nodes {
        number
        title
        body
        url
        createdAt
        updatedAt
        isDraft
        author { login }
        labels(first: 50) { nodes { name } }
        assignees(first: 20) { nodes { login } }
        comments(first: 100) {
          totalCount
          nodes {
            url
            body
            createdAt
            author { login }
            authorAssociation
            reactionGroups { content users { totalCount } }
          }
        }
        reviews(first: 50) {
          totalCount
          nodes {
            url
            body
            state
            submittedAt
            author { login }
            authorAssociation
            reactionGroups { content users { totalCount } }
          }
        }
        reviewThreads(first: 50) {
          totalCount
          nodes {
            isResolved
            comments(first: 100) {
              nodes {
                url
                body
                createdAt
                author { login }
                authorAssociation
                path
                position
                reactionGroups { content users { totalCount } }
              }
            }
          }
        }
        files(first: 100) {
          totalCount
          nodes { path additions deletions }
        }
        commits(last: 1) {
          nodes {
            commit {
              oid
              statusCheckRollup { state }
            }
          }
        }
      }
      pageInfo { hasNextPage endCursor }
    }
  }
}
`;

export function runGh(args: string[]): string {
  return execFileSync('gh', args, { encoding: 'utf8' });
}

export function runGraphql<T>(query: string, variables: Record<string, string>): T[] {
  const args = ['api', 'graphql', '--paginate', '-f', `query=${query}`];
  for (const [key, value] of Object.entries(variables)) {
    args.push('-F', `${key}=${value}`);
  }
  const output = runGh(args).trim();
  if (!output) {
    return [];
  }
  return output
    .split('\n')
    .filter(Boolean)
    .map((line) => JSON.parse(line) as T);
}

export function getRepo(): { owner: string; repo: string } {
  const raw = runGh(['repo', 'view', '--json', 'nameWithOwner']).trim();
  const parsed = JSON.parse(raw) as { nameWithOwner: string };
  const [owner, repo] = parsed.nameWithOwner.split('/');
  return { owner, repo };
}

export type IssuePage = { data: { repository: { issues: { nodes: GhIssueNode[] } } } };
export type PrPage = { data: { repository: { pullRequests: { nodes: GhPullRequestNode[] } } } };
