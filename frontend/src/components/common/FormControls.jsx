const CONTROL =
  'w-full rounded-lg border border-[var(--gridline)] bg-[var(--surface-2)] px-3 py-2.5 text-[var(--text-primary)] placeholder:text-[var(--text-muted)] outline-none transition-colors focus:border-[var(--primary)]'

const LABEL = 'mb-2 block text-sm font-medium text-[var(--text-primary)]'

/** Label + control pair. `name` doubles as the control id so the label always points at it. */
function Field({ name, label, children }) {
  return (
    <div>
      <label htmlFor={name} className={LABEL}>
        {label}
      </label>
      {children}
    </div>
  )
}

export function TextField({ name, label, ...props }) {
  return (
    <Field name={name} label={label}>
      <input id={name} name={name} className={CONTROL} {...props} />
    </Field>
  )
}

export function NumberField({ name, label, ...props }) {
  return (
    <TextField name={name} label={label} type="number" min="0" step="0.01" {...props} />
  )
}

export function SelectField({ name, label, options, ...props }) {
  return (
    <Field name={name} label={label}>
      <select id={name} name={name} className={CONTROL} {...props}>
        {options.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
    </Field>
  )
}

export function CheckboxField({ name, label, ...props }) {
  return (
    <label className="flex items-center gap-3 rounded-lg border border-[var(--gridline)] bg-[var(--surface-2)] px-3 py-2.5">
      <input
        type="checkbox"
        name={name}
        className="h-4 w-4 rounded border-[var(--gridline)] text-[var(--primary)] focus:ring-[var(--primary)]"
        {...props}
      />
      <span className="text-sm font-medium text-[var(--text-primary)]">{label}</span>
    </label>
  )
}

export function FormError({ children }) {
  if (!children) return null
  return (
    <div
      role="alert"
      className="rounded-lg border border-[var(--status-serious)]/30 bg-[var(--status-serious)]/10 px-3 py-2 text-sm text-[var(--status-serious)]"
    >
      {children}
    </div>
  )
}
