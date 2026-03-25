export const PROPERTY_TYPES = [
  { value: 'agriculture', label: 'Agriculture Farm' },
  { value: 'plot',        label: 'Plot' },
  { value: 'flat',        label: 'Flat' },
  { value: 'rent',        label: 'Rent' },
]

export const PROPERTY_TYPE_LABEL = Object.fromEntries(
  PROPERTY_TYPES.map(({ value, label }) => [value, label])
)
