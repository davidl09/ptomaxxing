import { useCallback, useEffect, useState } from 'react';

import PlannerForm from '../components/PlannerForm';
import PlanSummaryBar from '../components/PlanSummaryBar';
import BlocksList from '../components/BlocksList';
import LocalePicker from '../components/LocalePicker';
import { usePlanner } from '../hooks/usePlanner';

export default function PlannerPage() {
  const planner = usePlanner();
  const [selectedPlanIndex, setSelectedPlanIndex] = useState(0);
  const locale = navigator.language ?? 'en-CA';

  useEffect(() => {
    setSelectedPlanIndex(0);
  }, [planner.plans.length]);

  const selectedPlan = planner.plans[selectedPlanIndex];

  const handleCopy = useCallback(async (days: string[]) => {
    await navigator.clipboard.writeText(days.join('\n'));
  }, []);

  const handleLocaleChange = useCallback(
    (value: { country: string; region?: string; timezone: string }) => {
      planner.setParams({ ...planner.params, ...value });
    },
    [planner],
  );

  return (
    <main className="planner-page">
      <header>
        <h1>Max Days Off Planner</h1>
        <p>Find the best PTO strategy to maximize your time away from work.</p>
      </header>

      <LocalePicker
        country={planner.params.country}
        region={planner.params.region}
        timezone={planner.params.timezone}
        onChange={handleLocaleChange}
      />

      <PlannerForm params={planner.params} onSubmit={planner.submit} />

      {planner.error && <p role="alert">{planner.error}</p>}
      {planner.isLoading && <p role="status">Calculating plans…</p>}

      <section>
        <PlanSummaryBar
          plans={planner.plans}
          selectedIndex={selectedPlanIndex}
          onSelect={setSelectedPlanIndex}
          locale={locale}
        />
        {selectedPlan ? (
          <BlocksList
            plan={selectedPlan}
            onExport={(plan) => planner.downloadPlan(plan, `Plan ${String.fromCharCode(65 + selectedPlanIndex)}`)}
            onCopy={handleCopy}
            locale={locale}
          />
        ) : (
          <p>Select a plan to view details.</p>
        )}
      </section>

      {planner.alternates.length > 0 && (
        <section>
          <h2>Alternates</h2>
          <ul>
            {planner.alternates.map((plan, index) => (
              <li key={`alt-${index}`}>
                Plan {String.fromCharCode(65 + planner.plans.length + index)} — {plan.score.toFixed(1)} score
              </li>
            ))}
          </ul>
        </section>
      )}
    </main>
  );
}
