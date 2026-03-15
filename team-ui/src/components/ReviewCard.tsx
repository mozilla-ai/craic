import { forwardRef } from "react";
import type { KnowledgeUnit, Selection } from "../types";
import { DomainTags } from "./DomainTags";
import { timeAgo } from "../utils";
import type { DragState, PointerHandlers } from "../hooks/useCardDrag";
import { BADGE_APPEAR_RATIO, MAX_ROTATION_DEG } from "../hooks/useCardDrag";

interface Props {
  unit: KnowledgeUnit;
  selection: Selection;
  drag: DragState;
  pointerHandlers: PointerHandlers;
}

const CARD_STYLES: Record<string, string> = {
  neutral: "border-gray-200 bg-white",
  approve: "border-green-300 bg-green-50",
  reject: "border-red-300 bg-red-50",
  skip: "border-slate-400 bg-slate-50",
};

const ACTION_BOX_STYLES: Record<string, string> = {
  neutral: "bg-indigo-50 border-indigo-500 text-indigo-500",
  approve: "bg-green-50 border-green-500 text-green-600",
  reject: "bg-red-50 border-red-500 text-red-600",
  skip: "bg-slate-50 border-slate-400 text-slate-500",
};

const BADGE_CONFIG: Record<string, { symbol: string; bg: string }> = {
  approve: { symbol: "\u2713", bg: "bg-green-600" },
  reject: { symbol: "\u2715", bg: "bg-red-600" },
  skip: { symbol: "\u2014", bg: "bg-slate-600" },
};

function confidenceColor(c: number): string {
  if (c < 0.3) return "text-red-600";
  if (c < 0.5) return "text-amber-600";
  if (c < 0.7) return "text-yellow-500";
  return "text-green-600";
}

export const ReviewCard = forwardRef<HTMLDivElement, Props>(
  function ReviewCard({ unit, selection, drag, pointerHandlers }, ref) {
    const activeState = drag.isDragging ? drag.dragAction : selection;
    const cardStyle = CARD_STYLES[activeState ?? "neutral"];
    const actionBoxStyle = ACTION_BOX_STYLES[activeState ?? "neutral"];

    const rotation = drag.isDragging
      ? (drag.offset.x / 300) * MAX_ROTATION_DEG
      : 0;
    const shadowScale = drag.isDragging ? 1 + drag.dragProgress * 0.5 : 1;
    const transform = `translate(${drag.offset.x}px, ${drag.offset.y}px) rotate(${rotation}deg)`;
    const transition = drag.isDragging ? "none" : "transform 200ms ease-out, box-shadow 200ms ease-out";
    const shadow = `0 ${4 * shadowScale}px ${20 * shadowScale}px rgba(0,0,0,${0.08 * shadowScale})`;

    const badgeAction = drag.isDragging ? drag.dragAction : null;
    const showBadge = badgeAction && drag.dragProgress >= BADGE_APPEAR_RATIO;
    const badgeOpacity = showBadge
      ? Math.min((drag.dragProgress - BADGE_APPEAR_RATIO) / (1 - BADGE_APPEAR_RATIO), 1)
      : 0;
    const badge = badgeAction ? BADGE_CONFIG[badgeAction] : null;

    const badgePosition = (): React.CSSProperties => {
      if (!badgeAction) return {};
      if (badgeAction === "approve") return { top: "50%", right: "-14px", transform: "translateY(-50%)" };
      if (badgeAction === "reject") return { top: "50%", left: "-14px", transform: "translateY(-50%)" };
      return { top: "-14px", left: "50%", transform: "translateX(-50%)" };
    };

    return (
      <div
        ref={ref}
        className={`relative border-2 rounded-lg p-6 max-w-xl mx-auto select-none touch-none ${cardStyle}`}
        style={{ transform, transition, boxShadow: shadow }}
        {...pointerHandlers}
      >
        {showBadge && badge && (
          <div
            className={`absolute w-7 h-7 ${badge.bg} rounded-full flex items-center justify-center text-white text-base`}
            style={{ ...badgePosition(), opacity: badgeOpacity, transition: "opacity 100ms ease-out" }}
          >
            {badge.symbol}
          </div>
        )}

        <div className="flex items-center justify-between mb-3">
          <DomainTags domains={unit.domain} variant={activeState} />
          <span className="text-xs text-gray-400">
            {timeAgo(unit.evidence.first_observed)}
          </span>
        </div>

        <h2 className="text-lg font-semibold text-gray-900 mb-2">
          {unit.insight.summary}
        </h2>

        <p className="text-gray-600 mb-3 leading-relaxed">
          {unit.insight.detail}
        </p>

        <div className={`border-l-3 rounded-r-lg px-4 py-3 mb-6 ${actionBoxStyle}`}>
          <span className="text-xs font-semibold uppercase tracking-wide">
            Action
          </span>
          <p className="text-gray-800 text-sm mt-1">{unit.insight.action}</p>
        </div>

        <div className="flex gap-4 text-sm text-gray-500">
          <span>
            Confidence: <strong className={confidenceColor(unit.evidence.confidence)}>{unit.evidence.confidence.toFixed(2)}</strong>
          </span>
          <span>
            Confirmations: <strong className="text-gray-800">{unit.evidence.confirmations}</strong>
          </span>
        </div>
      </div>
    );
  },
);
