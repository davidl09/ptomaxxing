import { dateRangeDays } from '../utils/date';

interface MiniMonthStripProps {
  start: string;
  end: string;
  pto: string[];
  holidays: string[];
  weekends: string[];
}

export default function MiniMonthStrip({ start, end, pto, holidays, weekends }: MiniMonthStripProps) {
  const days = dateRangeDays(start, end);
  return (
    <div className="mini-month-strip" role="list" aria-label="Calendar strip">
      {days.map((day) => {
        const role = holidays.includes(day) ? 'Holiday' : weekends.includes(day) ? 'Weekend' : pto.includes(day) ? 'PTO' : 'Off';
        return (
          <span key={day} role="listitem" aria-label={`${day} ${role}`} className={`day ${role.toLowerCase()}`}>
            {day.slice(-2)}
          </span>
        );
      })}
      <div className="legend" aria-hidden="true">
        <span className="day pto">PTO</span>
        <span className="day weekend">Weekend</span>
        <span className="day holiday">Holiday</span>
      </div>
    </div>
  );
}
