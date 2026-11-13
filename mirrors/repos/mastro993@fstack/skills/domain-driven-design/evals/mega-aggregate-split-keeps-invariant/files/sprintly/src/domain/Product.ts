export class ConcurrencyError extends Error {}

export interface BacklogItem {
  id: string;
  title: string;
  story: string;
  estimate?: number;
  sprintId?: string;
  releaseId?: string;
}

export interface Sprint {
  id: string;
  name: string;
  starts: Date;
  ends: Date;
  capacity: number;
}

export interface Release {
  id: string;
  name: string;
  date: Date;
}

export class Product {
  constructor(
    readonly id: string,
    public name: string,
    public backlogItems: BacklogItem[],
    public sprints: Sprint[],
    public releases: Release[],
    public version: number,
  ) {}

  planBacklogItem(item: BacklogItem): void {
    this.backlogItems.push(item);
  }

  editBacklogItem(itemId: string, title: string, story: string): void {
    const item = this.item(itemId);
    item.title = title;
    item.story = story;
  }

  estimate(itemId: string, points: number): void {
    this.item(itemId).estimate = points;
  }

  commitToSprint(itemId: string, sprintId: string): void {
    const item = this.item(itemId);
    const sprint = this.sprints.find(s => s.id === sprintId);
    if (!sprint) throw new Error("no such sprint");
    if (item.estimate === undefined) throw new Error("estimate the item before committing it");

    const committed = this.backlogItems
      .filter(i => i.sprintId === sprintId)
      .reduce((sum, i) => sum + (i.estimate ?? 0), 0);
    if (committed + item.estimate > sprint.capacity) {
      throw new Error("sprint is over capacity");
    }
    item.sprintId = sprintId;
  }

  scheduleSprint(sprint: Sprint): void {
    this.sprints.push(sprint);
  }

  scheduleRelease(release: Release): void {
    this.releases.push(release);
  }

  private item(itemId: string): BacklogItem {
    const item = this.backlogItems.find(i => i.id === itemId);
    if (!item) throw new Error("no such backlog item");
    return item;
  }
}
