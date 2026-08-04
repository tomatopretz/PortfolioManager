import SegmentedControl from '../common/SegmentedControl'
import { TIME_RANGES } from '../../constants/portfolio'

const OPTIONS = TIME_RANGES.map(({ key, label }) => ({ value: key, label }))

function TimeRangeFilter({ timeRange, onTimeRangeChange }) {
  return (
    <SegmentedControl
      ariaLabel="Performance time range"
      options={OPTIONS}
      value={timeRange}
      onChange={onTimeRangeChange}
    />
  )
}

export default TimeRangeFilter
