import type { Plan } from '../api/types';
import { formatDateRange } from '../utils/date';

interface PlanSummaryBarProps {
  plans: Plan[];
  selectedIndex: number;
  onSelect: (index: number) => void;
  locale: string;
}

export default function PlanSummaryBar({ plans, selectedIndex, onSelect, locale }: PlanSummaryBarProps) {
  if (!plans.length) {
    return <p role="status">No plans available yet.</p>;
  }

  return (
    <nav aria-label="Plan summaries" className="plan-summary-bar">
      <ul>
        {plans.map((plan, index) => {
          const firstBlock = plan.blocks[0];
          const label = `Plan ${String.fromCharCode(65 + index)}: ${plan.score.toFixed(1)} score`;
          return (
            <li key={label}>
              <button
                type="button"
                className={selectedIndex === index ? 'active' : ''}
                onClick={() => onSelect(index)}
                aria-pressed={selectedIndex === index}
              >
                <span className="label">Plan {String.fromCharCode(65 + index)}</span>
                <span className="details">
                  {`${plan.pto_used} PTO • ${plan.blocks.length} blocks • ${formatDateRange(firstBlock.start, firstBlock.end, locale)}`}
                </span>
              </button>
            </li>
          );
        })}
      </ul>
    </nav>
  );
}
