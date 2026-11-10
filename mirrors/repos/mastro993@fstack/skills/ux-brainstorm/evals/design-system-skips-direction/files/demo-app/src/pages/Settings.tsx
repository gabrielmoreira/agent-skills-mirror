import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardTitle } from "@/components/ui/card";
import { Switch } from "@/components/ui/switch";
import type { WorkspaceSettings } from "@/lib/settings";

// Everything on one long page. Managers say they can't find anything.
export function SettingsPage({ initial }: { initial: WorkspaceSettings }) {
  const [s, setS] = useState(initial);

  return (
    <div className="mx-auto max-w-3xl space-y-6 p-8">
      <h1 className="text-2xl font-semibold">Settings</h1>
      <p className="text-muted-foreground">
        Here you can configure all of the settings for your workspace. Changes that you make on this page will
        apply to every location in your workspace and to every member of your team, so please review them carefully
        before you click the Save Changes button at the bottom of the page.
      </p>

      <Card>
        <CardTitle>General Workspace Information and Regional Preferences</CardTitle>
        <label className="mt-4 block text-sm">Please enter the name of your workspace</label>
        <input className="mt-1 w-full rounded-md border p-2" value={s.workspaceName} onChange={(e) => setS({ ...s, workspaceName: e.target.value })} />
        <label className="mt-4 block text-sm">Please select the timezone that your workspace operates in</label>
        <input className="mt-1 w-full rounded-md border p-2" value={s.timezone} readOnly />
      </Card>

      <Card>
        <CardTitle>Locations</CardTitle>
        {s.locations.map((l) => (
          <div key={l.id} className="mt-3 flex items-center justify-between">
            <div>
              <div>{l.name}</div>
              <div className="text-sm text-muted-foreground">{l.address}</div>
            </div>
            <div className="flex gap-2">
              <Button variant="outline" size="sm">Edit this location</Button>
              <Button variant="destructive" size="sm">Delete this location</Button>
            </div>
          </div>
        ))}
      </Card>

      <Card>
        <CardTitle>Scheduling Rules and Policies</CardTitle>
        <div className="mt-4 flex items-center justify-between">
          <span>Allow employees to swap their shifts with other employees</span>
          <Switch checked={s.scheduling.allowShiftSwaps} />
        </div>
        <div className="mt-4 flex items-center justify-between">
          <span>Require a manager to approve shift swaps before they take effect</span>
          <Switch checked={s.scheduling.swapsNeedApproval} />
        </div>
      </Card>

      <Card>
        <CardTitle>Notification Preferences</CardTitle>
        {Object.entries(s.notifications).map(([key, n]) => (
          <div key={key} className="mt-4 grid grid-cols-4 items-center">
            <span>{key}</span>
            <label><input type="checkbox" checked={n.email} readOnly /> Send an email</label>
            <label><input type="checkbox" checked={n.push} readOnly /> Send a push notification</label>
            <label><input type="checkbox" checked={n.sms} readOnly /> Send a text message</label>
          </div>
        ))}
      </Card>

      <Card>
        <CardTitle>Billing</CardTitle>
        <p className="mt-2">You are on the {s.billing.plan} plan using {s.billing.seatsUsed} of {s.billing.seats} seats.</p>
      </Card>

      <Button className="w-full">Save Changes</Button>
    </div>
  );
}
