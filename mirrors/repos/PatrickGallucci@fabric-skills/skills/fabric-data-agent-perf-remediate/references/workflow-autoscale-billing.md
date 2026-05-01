# Workflow: Autoscale Billing and SKU Right-Sizing

## Table of Contents

- [When to Consider Autoscale](#when-to-consider-autoscale)
- [Enabling Autoscale Billing](#enabling-autoscale-billing)
- [SKU Right-Sizing After Autoscale](#sku-right-sizing-after-autoscale)
- [Monitoring Costs](#monitoring-costs)
- [Quota Management](#quota-management)

## When to Consider Autoscale

Autoscale Billing for Spark is beneficial when:
- Spark workloads contend with other Fabric workloads (Power BI, Data Warehouse) for capacity
- Data Agent Spark jobs are throttled due to concurrent non-agent workloads
- You want pay-as-you-go billing instead of reserved capacity for Spark
- Spark usage is bursty and doesn't justify a large fixed SKU

**Cost model:** 0.5 CU Hour per Spark job, billed only during active execution (no idle costs).

## Enabling Autoscale Billing

**Requirements:**
- F-SKU only (F2 and above) — not P-SKU or Trial
- Fabric Capacity Administrator role

**Steps:**
1. Navigate to **Admin Portal** > **Governance and insights** > **Admin portal**.
2. Select **Capacity settings** > **Fabric capacity** tab.
3. Select the target capacity.
4. Scroll to **Autoscale Billing for Fabric Spark**.
5. Enable the toggle.
6. Set Maximum Capacity Units via slider (limited by Azure subscription quota).
7. Click **Save**.

**Warning:** Enabling, disabling, or reducing max CU will cancel ALL active Spark jobs running
under Autoscale Billing.

## SKU Right-Sizing After Autoscale

After moving Spark workloads to Autoscale Billing, you can downsize the shared capacity SKU:

1. Go to **Azure Portal**.
2. Search for and select your Fabric capacity resource.
3. Click **Pause** to temporarily stop the capacity (clears unsmoothed Spark usage).
4. Wait 5 minutes.
5. Click **Resume** to restart.
6. Resize the capacity to a lower SKU sized for remaining workloads (Power BI, Data Warehouse, Real-Time Intelligence).

**Note:** Only Azure administrators can resize SKUs. This is done in the Azure portal, not Fabric.

## Monitoring Costs

### Azure Cost Analysis

1. Navigate to **Azure Portal** > **Subscriptions** > select subscription.
2. Go to **Cost Analysis**.
3. Filter by resource: your Fabric capacity.
4. Use meter: `Autoscale for Spark Capacity Usage CU`.
5. View real-time compute spend for Spark workloads.

### Premium Metrics App

Install the Premium Metrics App for detailed capacity utilization dashboards that show:
- Per-workload capacity consumption
- Peak utilization periods
- Throttling events
- Historical usage trends

## Quota Management

The maximum CU slider is limited by your Azure subscription quota. To increase:

1. Navigate to **Azure Portal** > **Quotas**.
2. Find the Fabric capacity quota for your region.
3. Submit a quota increase request.
4. Once approved, the new limits are reflected in the Autoscale Billing slider.
