<script lang="ts">
  interface Props {
    title: string;
    initialCount?: number;
  }
  let { title, initialCount = 0 }: Props = $props();

  let count = $state(initialCount);
  let isPositive = $derived(count > 0);

  function increment() {
    count += 1;
  }
</script>

<article class="svelte-card">
  <h3>{title}</h3>
  <p>Current Telemetry Metric: <strong class:positive={isPositive}>{count}</strong></p>
  <button type="button" class="btn" onclick={increment}>
    Increment Counter
  </button>
</article>

<style>
  .svelte-card {
    background: var(--card, #0f172a);
    border: 1px solid var(--border, #1e293b);
    border-radius: 8px;
    padding: 1.5rem;
    color: var(--foreground, #f8fafc);
  }
  .positive {
    color: #4ade80;
  }
  .btn {
    min-height: 44px;
    padding: 0.5rem 1rem;
    background: var(--primary, #3b82f6);
    color: #ffffff;
    border: none;
    border-radius: 6px;
    cursor: pointer;
  }
</style>
