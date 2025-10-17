interface LocalePickerProps {
  country: string;
  region?: string;
  timezone: string;
  onChange: (value: { country: string; region?: string; timezone: string }) => void;
}

const COUNTRIES = [
  { code: 'CA', label: 'Canada', regions: ['ON', 'BC', 'QC'] },
  { code: 'US', label: 'United States', regions: ['CA', 'NY', 'TX'] },
  { code: 'GB', label: 'United Kingdom', regions: ['ENG', 'SCT'] },
];

export default function LocalePicker({ country, region, timezone, onChange }: LocalePickerProps) {
  const selectedCountry = COUNTRIES.find((item) => item.code === country) ?? COUNTRIES[0];

  return (
    <fieldset className="locale-picker">
      <legend>Locale</legend>
      <label>
        Country
        <select
          value={selectedCountry.code}
          onChange={(event) =>
            onChange({ country: event.target.value, region, timezone })
          }
        >
          {COUNTRIES.map((item) => (
            <option key={item.code} value={item.code}>
              {item.label}
            </option>
          ))}
        </select>
      </label>
      <label>
        Region
        <select
          value={region ?? ''}
          onChange={(event) => onChange({ country: selectedCountry.code, region: event.target.value, timezone })}
        >
          <option value="">--</option>
          {selectedCountry.regions.map((item) => (
            <option key={item} value={item}>
              {item}
            </option>
          ))}
        </select>
      </label>
      <label>
        Timezone
        <input value={timezone} onChange={(event) => onChange({ country: selectedCountry.code, region, timezone: event.target.value })} />
      </label>
    </fieldset>
  );
}
