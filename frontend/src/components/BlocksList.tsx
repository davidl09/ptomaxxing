import type { Plan } from '../api/types';
import { formatDateRange } from '../utils/date';
import MiniMonthStrip from './MiniMonthStrip';

interface BlocksListProps {
  plan: Plan;
  onExport: (plan: Plan) => void;
  onCopy: (days: string[]) => void;
  locale: string;
}

export default function BlocksList({ plan, onExport, onCopy, locale }: BlocksListProps) {
  if (!plan.blocks.length) {
    return <p role="status">No blocks available.</p>;
  }

  return (
    <section aria-label="Plan blocks" className="blocks-list">
      {plan.blocks.map((block) => (
        <article key={`${block.start}-${block.end}`} className="block-card">
          <header>
            <h3>{formatDateRange(block.start, block.end, locale)}</h3>
            <p>{`${block.days_off} days off • ${block.pto.length} PTO`}</p>
          </header>
          <p>{block.explain}</p>
          <MiniMonthStrip start={block.start} end={block.end} pto={block.pto} holidays={block.holidays} weekends={block.weekends} />
          <footer>
            <button type="button" onClick={() => onExport(plan)}>
              Add to calendar
            </button>
            <button type="button" onClick={() => onCopy(block.pto)}>
              Copy PTO days
            </button>
          </footer>
        </article>
      ))}
    </section>
  );
}
