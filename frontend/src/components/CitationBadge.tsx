import { useState } from 'react';

interface CitationBadgeProps {
  paperTitle: string;
  section: string;
  tooltip: string;
}

export default function CitationBadge({ paperTitle, section, tooltip }: CitationBadgeProps) {
  const [showTooltip, setShowTooltip] = useState(false);

  return (
    <span
      className="citation-badge"
      onMouseEnter={() => setShowTooltip(true)}
      onMouseLeave={() => setShowTooltip(false)}
    >
      [{paperTitle}, §{section}]
      {showTooltip && (
        <span className="citation-tooltip">{tooltip}</span>
      )}
    </span>
  );
}
